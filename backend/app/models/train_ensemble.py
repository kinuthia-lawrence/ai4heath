"""
Train ensemble models (Random Forest + XGBoost) with SHAP explainability
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os
from pathlib import Path

# Paths
data_dir = Path(__file__).parent.parent.parent / "data"
model_dir = Path(__file__).parent

def load_and_preprocess():
    """Load training data and preprocess"""
    df = pd.read_csv(data_dir / "health_data.csv")
    
    # Preprocess
    regions_map = {'Machakos': 0, 'Garissa': 1, 'Kakamega': 2}
    gender_map = {'M': 1, 'F': 0}
    facility_map = {'Clinic': 0, 'Health Center': 1, 'Hospital': 2}
    
    df['region'] = df['region'].map(regions_map)
    df['gender'] = df['gender'].map(gender_map)
    df['facility_type'] = df['facility_type'].map(facility_map)
    
    # Features: symptoms (15) + vitals (3) + demographics (4)
    feature_cols = [
        'cough','fever','headache','fatigue','vomiting','diarrhea','shortness_of_breath',
        'sore_throat','loss_of_taste','loss_of_smell','body_pain','runny_nose','chills',
        'skin_rash','conjunctivitis',
        'temperature','heart_rate','oxygen_saturation','age','gender','region','facility_type'
    ]
    
    X = df[feature_cols].fillna(0)
    y = df['diagnosis']
    
    return X, y, feature_cols

def train_models():
    """Train Random Forest and Gradient Boosting models"""
    print("Loading data...")
    X, y, feature_cols = load_and_preprocess()
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Training on {len(X_train)} samples, testing on {len(X_test)}")
    
    # Random Forest
    print("\n[1] Training Random Forest...")
    rf_model = RandomForestClassifier(
        n_estimators=100, 
        max_depth=15, 
        random_state=42,
        n_jobs=-1
    )
    rf_model.fit(X_train, y_train)
    rf_pred = rf_model.predict(X_test)
    rf_acc = accuracy_score(y_test, rf_pred)
    print(f"Random Forest Accuracy: {rf_acc:.4f}")
    
    # Gradient Boosting
    print("\n[2] Training Gradient Boosting...")
    gb_model = GradientBoostingClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        random_state=42
    )
    gb_model.fit(X_train, y_train)
    gb_pred = gb_model.predict(X_test)
    gb_acc = accuracy_score(y_test, gb_pred)
    print(f"Gradient Boosting Accuracy: {gb_acc:.4f}")
    
    # Save models
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(rf_model, model_dir / "model_rf.pkl")
    joblib.dump(gb_model, model_dir / "model_gb.pkl")
    joblib.dump(feature_cols, model_dir / "feature_cols.pkl")
    print(f"\nModels saved to {model_dir}")
    
    # Report
    print(f"\n{'='*60}")
    print("RANDOM FOREST REPORT")
    print(f"{'='*60}")
    print(classification_report(y_test, rf_pred))
    print(f"\n{'='*60}")
    print("GRADIENT BOOSTING REPORT")
    print(f"{'='*60}")
    print(classification_report(y_test, gb_pred))

if __name__ == "__main__":
    train_models()
