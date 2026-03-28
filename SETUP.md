## Setup & Execution Guide

### Step 1: Generate Outbreak-Biased Training Data
```bash
cd backend
python generate_data.py
```
This creates `data/health_data.csv` with 5000 cases featuring regional outbreak patterns:
- **Machakos**: 45% flu → outbreak signals with respiratory symptoms
- **Garissa**: 40% pneumonia → outbreak signals with respiratory symptoms  
- **Kakamega**: 50% malaria → outbreak signals with fever/chills patterns

### Step 2: Train Ensemble Models
```bash
python app/models/train_ensemble.py
```
Trains and saves:
- `app/models/model_rf.pkl` (Random Forest)
- `app/models/model_gb.pkl` (Gradient Boosting)
- `app/models/feature_cols.pkl` (feature column mapping)

Reports accuracy for both models.

### Step 3: Start Backend API
```bash
uvicorn app.main:app --reload
```
API runs on `http://localhost:8000`

### Step 4: Open Frontend
Open `frontend/index.html` in browser at `http://localhost:8000` or via LiveServer

## Frontend UX - Compact Design

**Header**: Blue banner with status indicator (green/red)

**Controls Row** (3 columns):
- PING button - Check API health
- OBVIOUS input + button - Generate 50 outbreak-pattern cases (default)
- RANDOM input + button - Generate 50 random-pattern cases (default)

**Feedback Toast**: Green notification appears when simulation completes ("✓ Generated 50 cases...")

**Prediction Button**: Large red "RUN ADVANCED PREDICTION" button

**Results Area** (scrollable):
1. **Prediction Summary** (5-column grid):
   - Dominant Disease, Outbreak Risk %, Risk Level, Confidence %, Total Cases
   - Summary interpretation text

2. **Disease Predictions** (3-column responsive grid):
   - Card per disease (malaria, flu, pneumonia, covid19, cholera, typhoid)
   - Status, Current/Forecast cases, Growth rate
   - **SHAP Drivers**: Top 3 features with impact weights (e.g., "fever: 35%")
   - Interpretation text (e.g., "High prevalence of respiratory symptoms...")

3. **Regional Predictions** (2-column responsive grid):
   - Card per region (Machakos, Garissa, Kakamega)
   - Dominant disease, Risk level, Current/Forecast cases
   - **SHAP Drivers**: Top disease features with impacts
   - Forecast text (e.g., "Likely increase in flu cases within 7 days...")

**Footer**: Risk legend (HIGH in red, MEDIUM in yellow, LOW in green)

## API Endpoints

### GET /ping
Health check
```json
{"message": "Pong"}
```

### POST /predict
Advanced prediction with explainability
```json
{
  "timestamp": "2026-03-28T14:22:45",
  "model": "Ensemble (Random Forest + Gradient Boosting)",
  "mode": "Batch Prediction + Short-Term Forecast",
  "explainability": "SHAP Aggregated Feature Contributions",
  "total_analyzed": 50,
  
  "prediction_summary": {
    "current_dominant_disease": "flu",
    "outbreak_probability": 0.65,
    "growth_signal": "positive",
    "risk_level": "HIGH",
    "confidence_score": 0.87,
    "prediction_window": "Next 7 days",
    "summary": "Model predicts HIGH likelihood of flu outbreak..."
  },
  
  "disease_predictions": {
    "flu": {
      "current_cases": 16,
      "predicted_cases_next_window": 20,
      "growth_rate": 0.45,
      "prediction_confidence": 0.89,
      "status": "OUTBREAK LIKELY",
      "top_shap_drivers": [
        {"feature": "cough", "mean_impact": 0.32},
        {"feature": "runny_nose", "mean_impact": 0.27},
        {"feature": "headache", "mean_impact": 0.19}
      ],
      "interpretation": "High prevalence of respiratory symptoms..."
    },
    ...other diseases...
  },
  
  "regional_predictions": [
    {
      "region": "Machakos",
      "current_cases": 22,
      "predicted_cases_next_window": 27,
      "dominant_disease": "flu",
      "outbreak_probability": 0.78,
      "risk_level": "HIGH",
      "top_shap_drivers": [...],
      "forecast": "Likely increase in flu cases within 7 days..."
    },
    ...other regions...
  ]
}
```

### POST /simulate-batch-obvious
Generate clear outbreak pattern cases
```bash
/simulate-batch-obvious?size=50
```
Response:
```json
{
  "status": "success",
  "message": "✓ Generated 50 cases with OBVIOUS patterns",
  "cases_generated": 50,
  "ready_for_prediction": true
}
```

### POST /simulate-batch-random
Generate random symptom cases
```bash
/simulate-batch-random?size=50
```

## Key Features

✅ **Outbreak Bias**: Data weighted by region (flu→Machakos, malaria→Kakamega, pneumonia→Garissa)

✅ **Ensemble Predictions**: Random Forest + Gradient Boosting with probability averaging

✅ **SHAP Explainability**: Top 3 feature drivers per disease with impact weights

✅ **Growth Forecasting**: 7-day case projections based on current prevalence patterns

✅ **Risk Levels**: HIGH (≥40%), MEDIUM (20-39%), LOW (<20%)

✅ **Regional Analysis**: Separate predictions per region with disease-specific signals

✅ **Compact UI**: Small buttons, result grids, fits in viewport height

✅ **Live Feedback**: Green toast shows "✓ Generated X cases..." after simulation

## Disease-Feature Mappings (SHAP Drivers)

- **Flu**: cough (0.32), runny_nose (0.27), headache (0.19)
- **Malaria**: fever (0.35), chills (0.30), body_pain (0.22)
- **Pneumonia**: shortness_of_breath (0.36), cough (0.28), fever (0.20)
- **Cholera**: diarrhea (0.38), vomiting (0.33), fatigue (0.15)
- **Typhoid**: fever (0.33), headache (0.28), fatigue (0.21)
- **COVID-19**: loss_of_taste (0.32), loss_of_smell (0.30), fever (0.18)

## Status Values

- **OUTBREAK LIKELY**: Growth ≥40% - Red alert (growth_rate ≥ 0.40)
- **RISING**: Growth 25-39% - Orange (growth_rate 0.25-0.39)
- **MONITOR**: Growth 10-24% - Yellow (growth_rate 0.10-0.24)
- **STABLE**: Growth 0-9% - Green (growth_rate 0.01-0.09)
- **LOW ACTIVITY**: No cases - Blue (growth_rate = 0.0)
