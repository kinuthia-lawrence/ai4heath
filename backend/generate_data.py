import csv
import random
from datetime import datetime, timedelta

regions = ["Nairobi", "Kisumu", "Mombasa", "Nakuru", "Eldoret", "Machakos", "Meru", "Garissa", "Kakamega", "Kitale"]
facility_types = ["Hospital", "Clinic", "Health Center"]
genders = ["M", "F"]

symptom_fields = [
    "cough", "fever", "headache", "fatigue", "vomiting", "diarrhea",
    "shortness_of_breath", "sore_throat", "loss_of_taste",
    "loss_of_smell", "body_pain", "runny_nose", "chills",
    "skin_rash", "conjunctivitis"
]

def random_symptoms():
    return [s for s in symptom_fields if random.random() < 0.2]

def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))

# -------------------------
# CLINICAL LOGIC
# -------------------------
def generate_temperature(symptoms):
    if "fever" in symptoms:
        return round(random.uniform(37.5, 40.5), 1)
    return round(random.uniform(36.0, 37.4), 1)

def generate_oxygen(symptoms):
    if "shortness_of_breath" in symptoms:
        return round(random.uniform(85, 94), 1)
    return round(random.uniform(95, 100), 1)

def generate_heart_rate(symptoms):
    if "fever" in symptoms:
        return random.randint(90, 120)
    return random.randint(60, 100)

def generate_diagnosis(symptoms):
    if "fever" in symptoms and "chills" in symptoms:
        return "malaria"
    elif "cough" in symptoms and "shortness_of_breath" in symptoms:
        return "pneumonia"
    elif "loss_of_taste" in symptoms or "loss_of_smell" in symptoms:
        return "covid19"
    elif "diarrhea" in symptoms and "vomiting" in symptoms:
        return "cholera"
    elif "fever" in symptoms and "headache" in symptoms:
        return "typhoid"
    else:
        return "flu"

def generate_risk(symptoms, temperature, age, oxygen):
    score = 0

    if temperature > 39:
        score += 2
    if oxygen < 92:
        score += 3
    if "shortness_of_breath" in symptoms:
        score += 2
    if "vomiting" in symptoms or "diarrhea" in symptoms:
        score += 1
    if age > 60:
        score += 2

    if score >= 5:
        return "High"
    elif score >= 3:
        return "Medium"
    else:
        return "Low"

def generate_outcome(risk):
    if risk == "High":
        return random.choices(["recovered", "admitted", "deceased"], [0.5, 0.4, 0.1])[0]
    elif risk == "Medium":
        return random.choices(["recovered", "admitted"], [0.7, 0.3])[0]
    else:
        return "recovered"

# -------------------------
# DATASET
# -------------------------
header = [
    "record_id", "age", "gender", "visit_date", "region", "facility_type",
    "temperature", "heart_rate", "oxygen_saturation",
    "diagnosis", "risk_level"
] + symptom_fields + ["outcome"]

with open("data/health_data.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(header)

    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)

    for i in range(1, 5001):
        age = random.randint(1, 90)
        gender = random.choice(genders)
        visit_date = random_date(start_date, end_date).strftime("%Y-%m-%d")
        region = random.choice(regions)
        facility_type = random.choice(facility_types)

        symptoms = random_symptoms()

        temperature = generate_temperature(symptoms)
        oxygen = generate_oxygen(symptoms)
        heart_rate = generate_heart_rate(symptoms)

        diagnosis = generate_diagnosis(symptoms)
        risk = generate_risk(symptoms, temperature, age, oxygen)
        outcome = generate_outcome(risk)

        symptom_bools = [1 if s in symptoms else 0 for s in symptom_fields]

        row = [
            i, age, gender, visit_date, region, facility_type,
            temperature, heart_rate, oxygen,
            diagnosis, risk
        ] + symptom_bools + [outcome]

        writer.writerow(row)

print("Generated data/health_data.csv successfully!")