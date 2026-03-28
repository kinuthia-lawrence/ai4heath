from fastapi import APIRouter
import pandas as pd
import numpy as np
import os
from datetime import datetime
import joblib
from pathlib import Path
import shap
from collections import Counter, defaultdict

router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "Welcome to the AI4Health API"}
    
@router.get("/ping")
def ping():
    return {"message": "Pong"}

@router.post("/predict")
def batch_report():
    # Paths
    model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'model.pkl')
    batch_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'batch_data.csv')
    if not Path(model_path).exists():
        return {"error": "Model not found. Train the model first."}
    if not Path(batch_path).exists():
        return {"error": "No batch data found. Simulate a batch first."}
    model = joblib.load(model_path)
    df = pd.read_csv(batch_path)
    # Preprocess: encode categorical as in training
    for col, mapping in {
        'gender': {'M': 1, 'F': 0},
        'region': {'Machakos': 0, 'Garissa': 1, 'Kakamega': 2},
        'facility_type': {'Clinic': 0, 'Health Center': 1, 'Hospital': 2}
    }.items():
        if col in df:
            df[col] = df[col].map(mapping).fillna(-1).astype(int)
    feature_cols = [
        'cough','fever','headache','fatigue','vomiting','diarrhea','shortness_of_breath',
        'sore_throat','loss_of_taste','loss_of_smell','body_pain','runny_nose','chills',
        'skin_rash','conjunctivitis',
        'temperature','heart_rate','oxygen_saturation','age','gender','region','facility_type'
    ]
    X = df[feature_cols]
    preds = model.predict(X)
    known_diseases = set(model.classes_)
       # SHAP explainability
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    # Combine predictions and explanations
    patient_reports = []
    for i, row in enumerate(X.values):
        pred_class = preds[i]
        explanation = []
        if isinstance(shap_values, list):  # multiclass
            if pred_class in known_diseases:
                class_idx = list(model.classes_).index(pred_class)
                if class_idx < len(shap_values) and i < len(shap_values[class_idx]):
                    shap_row = shap_values[class_idx][i]
                    top_features_idx = np.argsort(np.abs(shap_row))[-3:][::-1]
                    feature_names = [feature_cols[j] for j in top_features_idx]
                    feature_impacts = [float(shap_row[j]) for j in top_features_idx]
                    explanation = list(zip(feature_names, feature_impacts))
        else:  # binary or regression
            if i < len(shap_values):
                shap_row = shap_values[i]
                top_features_idx = np.argsort(np.abs(shap_row))[-3:][::-1]
                feature_names = [feature_cols[j] for j in top_features_idx]
                feature_impacts = [float(shap_row[j]) for j in top_features_idx]
                explanation = list(zip(feature_names, feature_impacts))
        patient_reports.append({
            "row": i,
            "region": df.iloc[i]['region'],
            "prediction": pred_class if pred_class in known_diseases else "unknown_disease",
            "symptoms": {col: df.iloc[i][col] for col in feature_cols},
            "top_features": explanation
        })
    # Outbreak/trend detection
    region_counts = defaultdict(Counter)
    country_counts = Counter()
    for report in patient_reports:
        region = report["region"]
        pred = report["prediction"]
        region_counts[region][pred] += 1
        country_counts[pred] += 1
    # Outbreaks: threshold can be tuned
    outbreak_threshold = 5
    outbreaks = []
    for region, counts in region_counts.items():
        for disease, count in counts.items():
            if count >= outbreak_threshold:
                outbreaks.append({
                    "region": region,
                    "disease": disease,
                    "cases": count
                })
    # Countrywide outbreaks
    country_outbreaks = []
    for disease, count in country_counts.items():
        if count >= outbreak_threshold:
            country_outbreaks.append({
                "disease": disease,
                "cases": count
            })
    # Save for storage if needed
    pd.DataFrame(patient_reports).to_csv(os.path.join(os.path.dirname(batch_path), 'batch_report.csv'), index=False)
    return {
        "patients": patient_reports,
        "region_outbreaks": outbreaks,
        "country_outbreaks": country_outbreaks,
        "outbreak_threshold": outbreak_threshold
    }

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
BATCH_PATH = os.path.join(DATA_DIR, 'batch_data.csv')

@router.post("/simulate-batch")
def simulate_batch(size: int = 100):
    np.random.seed(int(datetime.now().timestamp()))
    columns = [
        'age','gender','region','facility_type','temperature','heart_rate','oxygen_saturation',
        'cough','fever','headache','fatigue','vomiting','diarrhea','shortness_of_breath',
        'sore_throat','loss_of_taste','loss_of_smell','body_pain','runny_nose','chills',
        'skin_rash','conjunctivitis'
    ]
    genders = ['M', 'F']
    regions = ['Machakos', 'Garissa', 'Kakamega']
    facilities = ['Clinic', 'Health Center', 'Hospital']
    data = []
    for _ in range(size):
        region = np.random.choice(regions, p=[0.5, 0.3, 0.2])  # More from Machakos
        # Bias: if region is Machakos, more likely to have fever/cough
        symptoms = np.random.randint(0, 2, size=15)
        if region == 'Machakos':
            symptoms[columns.index('fever')-4] = 1 if np.random.rand() < 0.7 else 0
            symptoms[columns.index('cough')-4] = 1 if np.random.rand() < 0.6 else 0
        row = [
            np.random.randint(0, 100),
            np.random.choice(genders),
            region,
            np.random.choice(facilities),
            np.round(np.random.uniform(36, 40), 1),
            np.random.randint(60, 120),
            np.round(np.random.uniform(90, 100), 1)
        ] + list(symptoms)
        data.append(row)
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(BATCH_PATH, index=False)
    return {"message": f"Simulated batch of {size} records saved to batch_data.csv"}