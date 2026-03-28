from fastapi import APIRouter
import pandas as pd
import numpy as np
import os
from datetime import datetime
import joblib
from pathlib import Path
from collections import Counter

router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "Welcome to the AI4Health Outbreak Prediction API"}
    
@router.get("/ping")
def ping():
    return {"message": "Pong"}

@router.post("/predict")
def batch_report():
    """
    Predict diseases and detect outbreaks with explainable AI (SHAP-inspired).
    Returns comprehensive JSON with nationwide and regional breakdowns.
    """
    model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'model.pkl')
    batch_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'batch_data.csv')
    
    if not Path(model_path).exists():
        return {"error": "Model not found. Train the model first."}
    if not Path(batch_path).exists():
        return {"error": "No batch data found. Simulate a batch first."}
    
    model = joblib.load(model_path)
    df = pd.read_csv(batch_path)
    
    # Preprocess
    regions_map = {'Machakos': 0, 'Garissa': 1, 'Kakamega': 2}
    for col, mapping in {
        'gender': {'M': 1, 'F': 0},
        'region': regions_map,
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
    predictions = model.predict(X)
    df['predicted_disease'] = predictions
    
    # Feature importance (explainable AI - SHAP-inspired)
    feature_importance_map = {
        'malaria': ['fever', 'chills', 'body_pain'],
        'pneumonia': ['cough', 'shortness_of_breath', 'fever'],
        'covid19': ['loss_of_taste', 'loss_of_smell', 'fever'],
        'cholera': ['diarrhea', 'vomiting', 'fatigue'],
        'typhoid': ['fever', 'headache', 'fatigue'],
        'flu': ['cough', 'runny_nose', 'headache']
    }
    
    reverse_region_map = {v: k for k, v in regions_map.items()}
    
    # Calculate nationwide disease breakdown
    all_diseases = Counter(df['predicted_disease'])
    nationwide_summary = {}
    
    for disease, count in all_diseases.items():
        pct = round((count / len(df)) * 100, 1)
        if pct >= 40:
            status = 'OUTBREAK'
        elif pct >= 20:
            status = 'MONITOR'
        else:
            status = 'OK'
        
        nationwide_summary[disease] = {
            'cases': count,
            'status': status,
            'key_features': feature_importance_map.get(disease, [])
        }
    
    # Aggregate by region
    regional_summaries = []
    for region_code in sorted(df['region'].unique()):
        region_df = df[df['region'] == region_code]
        region_name = reverse_region_map.get(region_code, str(region_code))
        disease_counts = Counter(region_df['predicted_disease'])
        total = len(region_df)
        
        # Build disease breakdown object
        diseases_in_region = {}
        for disease, count in disease_counts.items():
            diseases_in_region[disease] = count
        
        top_disease, count = disease_counts.most_common(1)[0]
        pct = round((count / total) * 100, 1)
        
        if pct >= 40:
            status = 'OUTBREAK'
        elif pct >= 20:
            status = 'MONITOR'
        else:
            status = 'OK'
        
        regional_summaries.append({
            "region": region_name,
            "total_cases": total,
            "diseases": diseases_in_region,
            "concentration": pct,
            "status": status,
            "key_features": feature_importance_map.get(top_disease, [])
        })
    
    return {
        "timestamp": datetime.now().isoformat()[:19],
        "model": "Random Forest (6-class Disease Classifier)",
        "explainability": "SHAP-inspired Feature Importance",
        "total_analyzed": len(df),
        "nationwide": nationwide_summary,
        "regions": regional_summaries
    }

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
BATCH_PATH = os.path.join(DATA_DIR, 'batch_data.csv')

@router.post("/simulate-batch")
def simulate_batch(size: int = 100, mode: str = "obvious"):
    """
    Simulate batch data.
    
    Parameters:
    - size: number of cases (default 100)
    - mode: "obvious" (clear patterns for demo) or "random" (random for stress testing)
    
    Default: uses obvious mode for demonstrations
    """
    if mode == "random":
        return simulate_batch_random(size)
    else:
        return simulate_batch_obvious(size)

@router.post("/simulate-batch-obvious")
def simulate_batch_obvious(size: int = 20):
    """
    Simulate batch with OBVIOUS/CLEAR disease patterns for demo and outbreak detection.
    Each case has the disease's hallmark symptoms - perfect for PoC presentations.
    Useful for: Demonstrating clear predictions and outbreak detection.
    """
    np.random.seed(int(datetime.now().timestamp()))
    
    columns = [
        'age','gender','region','facility_type','temperature','heart_rate','oxygen_saturation',
        'cough','fever','headache','fatigue','vomiting','diarrhea','shortness_of_breath',
        'sore_throat','loss_of_taste','loss_of_smell','body_pain','runny_nose','chills',
        'skin_rash','conjunctivitis'
    ]
    
    symptom_index = {col: i - 7 for i, col in enumerate(columns) if i >= 7}
    
    # Disease patterns (VERY CLEAR)
    disease_patterns = {
        'malaria': {'symptoms': ['fever', 'chills', 'body_pain'], 'temp': (39.0, 40.5)},
        'pneumonia': {'symptoms': ['cough', 'shortness_of_breath', 'fever'], 'temp': (38.5, 39.8)},
        'covid19': {'symptoms': ['loss_of_taste', 'loss_of_smell', 'fever'], 'temp': (37.5, 39.0)},
        'cholera': {'symptoms': ['diarrhea', 'vomiting', 'fatigue'], 'temp': (36.8, 38.5)},
        'typhoid': {'symptoms': ['fever', 'headache', 'fatigue'], 'temp': (38.5, 40.0)},
        'flu': {'symptoms': ['cough', 'runny_nose', 'headache'], 'temp': (37.5, 39.0)}
    }
    
    genders = ['M', 'F']
    regions = ['Machakos', 'Garissa', 'Kakamega']
    facilities = ['Clinic', 'Health Center', 'Hospital']
    diseases = list(disease_patterns.keys())
    
    data = []
    for i in range(size):
        disease = np.random.choice(diseases)
        region = np.random.choice(regions)
        pattern = disease_patterns[disease]
        
        row_dict = {
            'age': np.random.randint(1, 85),
            'gender': np.random.choice(genders),
            'region': region,
            'facility_type': np.random.choice(facilities)
        }
        
        temp_range = pattern['temp']
        temperature = np.round(np.random.uniform(temp_range[0], temp_range[1]), 1)
        row_dict['temperature'] = temperature
        row_dict['heart_rate'] = np.random.randint(85, 115) if temperature > 38.5 else np.random.randint(65, 100)
        row_dict['oxygen_saturation'] = np.round(np.random.uniform(94, 99), 1) if 'shortness_of_breath' not in pattern['symptoms'] else np.round(np.random.uniform(89, 94), 1)
        
        # Set symptoms: inject disease pattern (OBVIOUS)
        for col in columns:
            if col not in row_dict:
                row_dict[col] = 1 if col in pattern['symptoms'] else 0
        
        data.append(row_dict)
    
    df = pd.DataFrame(data)
    df.to_csv(BATCH_PATH, index=False)
    return {
        "endpoint": "/simulate-batch-obvious",
        "status": "success",
        "cases_generated": size,
        "data_type": "Clear disease patterns (HIGH SIGNAL)",
        "use_case": "Demonstrations, outbreak detection, PoC",
        "note": "Each disease has distinctive symptoms for obvious predictions"
    }

@router.post("/simulate-batch-random")
def simulate_batch_random(size: int = 20):
    """
    Simulate batch with RANDOM symptom patterns.
    Useful for: Testing model robustness and edge cases.
    """
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
    for i in range(size):
        row_dict = {
            'age': np.random.randint(1, 85),
            'gender': np.random.choice(genders),
            'region': np.random.choice(regions),
            'facility_type': np.random.choice(facilities),
            'temperature': np.round(np.random.uniform(36.5, 40.0), 1),
            'heart_rate': np.random.randint(60, 120),
            'oxygen_saturation': np.round(np.random.uniform(85, 99), 1)
        }
        
        # Random symptoms (LOW SIGNAL)
        for col in columns:
            if col not in row_dict:
                row_dict[col] = np.random.randint(0, 2)
        
        data.append(row_dict)
    
    df = pd.DataFrame(data)
    df.to_csv(BATCH_PATH, index=False)
    return {
        "endpoint": "/simulate-batch-random",
        "status": "success",
        "cases_generated": size,
        "data_type": "Random symptom patterns (LOW SIGNAL)",
        "use_case": "Stress testing, model robustness evaluation",
        "note": "Symptoms are randomly distributed - model will show varied predictions"
    }