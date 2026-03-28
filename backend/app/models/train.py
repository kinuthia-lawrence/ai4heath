# Model training pipeline for outbreak prediction

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder
import joblib
import os

def save_metrics_to_csv(report, path):
	# Convert classification report to DataFrame and save as CSV
	import csv
	import io
	# If report is a string, convert to dict
	if isinstance(report, str):
		from sklearn.metrics import classification_report as cr
		# Not possible to parse string directly, so re-calculate
		raise ValueError("Pass the classification_report with output_dict=True to save as CSV.")
	df = pd.DataFrame(report).transpose()
	df.to_csv(path)
	print(f"Validation metrics saved to {path}")

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'health_data.csv')
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.pkl')

def load_data(path=DATA_PATH):
	df = pd.read_csv(path)
	return df

def preprocess_data(df):
	# Handle missing values (simple fillna for demo)
	df = df.fillna(0)

	# Encode categorical variables
	label_encoders = {}
	for col in ['gender', 'region', 'facility_type']:
		le = LabelEncoder()
		df[col] = le.fit_transform(df[col])
		label_encoders[col] = le
	return df, label_encoders

def select_features_and_target(df, target='diagnosis'):
	# Features: all symptoms, vitals, age, gender, region, facility_type
	symptom_cols = [
		'cough','fever','headache','fatigue','vomiting','diarrhea','shortness_of_breath',
		'sore_throat','loss_of_taste','loss_of_smell','body_pain','runny_nose','chills',
		'skin_rash','conjunctivitis'
	]
	feature_cols = symptom_cols + [
		'temperature','heart_rate','oxygen_saturation','age','gender','region','facility_type'
	]
	X = df[feature_cols]
	y = df[target]
	return X, y

def train_and_evaluate(X, y):
	X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
	clf = RandomForestClassifier(n_estimators=100, random_state=42)
	clf.fit(X_train, y_train)
	y_pred = clf.predict(X_val)
	report_dict = classification_report(y_val, y_pred, output_dict=True)
	report_str = classification_report(y_val, y_pred)
	print('Validation Report:\n', report_str)
	return clf, report_dict

def save_model(model, path=MODEL_PATH):
	joblib.dump(model, path)
	print(f"Model saved to {path}")

def compute_risk_score(symptoms_dict, vitals_dict):
	"""Compute risk level (High/Medium/Low) based on symptoms and vitals."""
	score = 0
	
	# Symptom risk factors
	high_risk_symptoms = ['shortness_of_breath', 'vomiting', 'diarrhea']
	medium_risk_symptoms = ['fever', 'chills', 'fatigue']
	
	for symptom in high_risk_symptoms:
		if symptoms_dict.get(symptom) == 1:
			score += 3
	for symptom in medium_risk_symptoms:
		if symptoms_dict.get(symptom) == 1:
			score += 1
	
	# Vital signs risk factors
	temp = vitals_dict.get('temperature', 37)
	if temp > 39:
		score += 2
	elif temp > 38:
		score += 1
	
	ox = vitals_dict.get('oxygen_saturation', 95)
	if ox < 92:
		score += 3
	elif ox < 94:
		score += 1
	
	# Risk classification
	if score >= 5:
		return "High"
	elif score >= 2:
		return "Medium"
	else:
		return "Low"

def is_unusual_pattern(symptom_count, group_size):
	"""Flag if this symptom pattern is unusual (high concentration)."""
	# If more than 50% of a group has the same symptoms, it's unusual
	if symptom_count >= 3 and (symptom_count / group_size) > 0.5:
		return True
	return False

if __name__ == "__main__":
	df = load_data()
	df, label_encoders = preprocess_data(df)
	# Choose target: 'diagnosis' for disease prediction, 'risk_level' for risk prediction
	X, y = select_features_and_target(df, target='diagnosis')
	model, report = train_and_evaluate(X, y)
	save_model(model)
	# Save validation metrics to CSV
	metrics_path = os.path.join(os.path.dirname(__file__), 'validation_metrics.csv')
	save_metrics_to_csv(report, metrics_path)
