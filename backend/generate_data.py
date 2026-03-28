import csv
import random
from datetime import datetime, timedelta

regions = ["Machakos", "Garissa", "Kakamega"]
facilities = ["Hospital", "Clinic", "Health Center"]
genders = ["M", "F"]

symptom_fields = [
    "cough", "fever", "headache", "fatigue", "vomiting", "diarrhea",
    "shortness_of_breath", "sore_throat", "loss_of_taste",
    "loss_of_smell", "body_pain", "runny_nose", "chills",
    "skin_rash", "conjunctivitis"
]

def generate_disease_symptoms(diagnosis):
    """Generate CLEAR, OBVIOUS symptoms based on disease for strong training signal.
    
    Returns exactly 15 binary values corresponding to:
    cough(0), fever(1), headache(2), fatigue(3), vomiting(4), diarrhea(5),
    shortness_of_breath(6), sore_throat(7), loss_of_taste(8), loss_of_smell(9),
    body_pain(10), runny_nose(11), chills(12), skin_rash(13), conjunctivitis(14)
    """
    symptoms = [0] * 15
    
    if diagnosis == "malaria":
        # Malaria: fever + chills + body_pain
        symptoms[1] = 1   # fever
        symptoms[12] = 1  # chills
        symptoms[10] = 1  # body_pain
    elif diagnosis == "pneumonia":
        # Pneumonia: cough + shortness_of_breath + fever
        symptoms[0] = 1   # cough
        symptoms[6] = 1   # shortness_of_breath
        symptoms[1] = 1   # fever
    elif diagnosis == "covid19":
        # COVID: loss_of_taste + loss_of_smell + fever
        symptoms[8] = 1   # loss_of_taste
        symptoms[9] = 1   # loss_of_smell
        symptoms[1] = 1   # fever
    elif diagnosis == "cholera":
        # Cholera: diarrhea + vomiting + fatigue
        symptoms[5] = 1   # diarrhea
        symptoms[4] = 1   # vomiting
        symptoms[3] = 1   # fatigue
    elif diagnosis == "typhoid":
        # Typhoid: fever + headache + fatigue
        symptoms[1] = 1   # fever
        symptoms[2] = 1   # headache
        symptoms[3] = 1   # fatigue
    else:  # flu
        # Flu: cough + runny_nose + headache
        symptoms[0] = 1   # cough
        symptoms[11] = 1  # runny_nose
        symptoms[2] = 1   # headache
    
    return symptoms

def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))

# -------------------------
# CLINICAL LOGIC
# -------------------------
def generate_temperature(symptom_array):
    if symptom_array[1] == 1:  # fever is at index 1
        return round(random.uniform(37.5, 40.5), 1)
    return round(random.uniform(36.0, 37.4), 1)

def generate_oxygen(symptom_array):
    if symptom_array[6] == 1:  # shortness_of_breath is at index 6
        return round(random.uniform(85, 94), 1)
    return round(random.uniform(95, 100), 1)

def generate_heart_rate(symptom_array):
    if symptom_array[1] == 1:  # fever
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

def generate_risk(symptom_array, temperature, age, oxygen):
    score = 0
    # Map symptom indices to risk contributions
    if symptom_array[6] == 1:  # shortness_of_breath
        score += 2
    if symptom_array[4] == 1 or symptom_array[5] == 1:  # vomiting or diarrhea
        score += 1
    if temperature > 39:
        score += 2
    if oxygen < 92:
        score += 3
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
# OUTBREAK-BIAS DATASET (For demos - clear outbreak signal)
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

    # Regional outbreak distribution
    region_disease_weights = {
        "Machakos": {"flu": 0.45, "malaria": 0.30, "pneumonia": 0.15, "covid19": 0.05, "cholera": 0.03, "typhoid": 0.02},
        "Garissa": {"pneumonia": 0.40, "malaria": 0.35, "flu": 0.15, "covid19": 0.05, "typhoid": 0.03, "cholera": 0.02},
        "Kakamega": {"malaria": 0.50, "flu": 0.20, "cholera": 0.15, "pneumonia": 0.10, "covid19": 0.03, "typhoid": 0.02}
    }
    
    diseases = ["malaria", "pneumonia", "covid19", "cholera", "typhoid", "flu"]
    for i in range(1, 5001):
        age = random.randint(1, 90)
        gender = random.choice(genders)
        visit_date = random_date(start_date, end_date).strftime("%Y-%m-%d")
        region = random.choice(regions)
        facility_type = random.choice(facilities)

        # Use weighted disease distribution per region (outbreak bias)
        weights = region_disease_weights.get(region, {d: 1/6 for d in diseases})
        diseases_list = list(weights.keys())
        weights_list = list(weights.values())
        diagnosis = random.choices(diseases_list, weights=weights_list)[0]
        
        symptom_array = generate_disease_symptoms(diagnosis)

        temperature = generate_temperature(symptom_array)
        oxygen = generate_oxygen(symptom_array)
        heart_rate = generate_heart_rate(symptom_array)

        risk = generate_risk(symptom_array, temperature, age, oxygen)
        outcome = generate_outcome(risk)

        row = [
            i, age, gender, visit_date, region, facility_type,
            temperature, heart_rate, oxygen,
            diagnosis, risk
        ] + symptom_array + [outcome]

        writer.writerow(row)

print("Generated outbreak-biased data/health_data.csv with regional distributions!")