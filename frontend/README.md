# AI4Health Frontend - Setup Guide

## Overview
This is a modern, fancy frontend dashboard for the AI4Health Outbreak Prediction System. It provides:
- **API Health Monitoring** - Real-time ping checks
- **Data Simulation** - Two modes: obvious patterns (demo-ready) and random patterns (stress testing)
- **Prediction & Analysis** - Run disease predictions and detect outbreaks
- **Color-Coded Status Flags** - Visual indicators for outbreak severity
  - 🔴 **RED (OUTBREAK)** - ≥40% disease concentration
  - 🟡 **YELLOW (MONITOR)** - 20-39% concentration
  - 🟢 **GREEN (OK)** - <20% concentration

## Tech Stack
- **HTML5** - Structure and semantic markup
- **Tailwind CSS** - Modern utility-first styling
- **JavaScript (Vanilla)** - API interactions and DOM manipulation
- **Font Awesome** - Icon library for visual elements
- **Chart.js** - Data visualization (prepared for future enhancements)

## File Structure
```
frontend/
├── index.html          # Main dashboard UI
├── app.js              # API integration & interactivity
└── README.md           # This file
```

## Setup Instructions

### 1. Ensure Backend is Running
```bash
cd backend
pip install -r requirements.txt
python app/models/train.py      # Train the model if not already done
uvicorn app.main:app --reload   # Start API server on http://localhost:8000
```

### 2. Open Frontend
Simply open `frontend/index.html` in a modern web browser:
- Chrome, Firefox, Edge, Safari (all recent versions)
- Or use a local server if you prefer:
  ```bash
  cd frontend
  python -m http.server 8001
  # Open http://localhost:8001
  ```

## Features Walkthrough

### 1. API Status Monitor (Header)
- Displays real-time connection status to backend
- Green dot (✓) = API is healthy
- Red indicator (✗) = Connection error
- Auto-checks every 30 seconds

### 2. Simulation Cards

#### Obvious Patterns (Green Card)
- **Purpose**: Demo-ready data with clear disease signals
- **Use Case**: Hackathon presentations, proof-of-concept demos
- **Behavior**: 
  - Malaria: 60% of Machakos cases
  - COVID19: 60% of Garissa cases
  - Cholera: 60% of Kakamega cases
  - Each disease has distinctive symptom signatures
- **Result**: High disease concentration → Clear OUTBREAK alerts

#### Random Patterns (Purple Card)
- **Purpose**: Stress testing and robustness evaluation
- **Use Case**: Model validation, edge case testing
- **Behavior**: Random symptom distribution across all patients
- **Result**: Varied predictions, low concentration typically

### 3. Prediction Engine

#### How it Works
1. **Simulate Data** - Generate batch data using obvious or random mode
2. **Run Prediction** - Click "RUN PREDICTION" button
3. **See Results** - Nationwide and regional analysis with outbreak flags

#### Response Components

**Nationwide Summary**
- Shows all 6 diseases and their nationwide stats
- Color-coded status flags
- Key features for outbreak pathogens

**Regional Breakdown**
- Per-region disease distribution
- Concentration percentage
- OUTBREAK/MONITOR/OK status
- Top contributing symptoms

**Summary Statistics**
- Total cases analyzed
- Number of regions with outbreaks
- Analysis timestamp

## Status Flag Colors

| Status | Color | Concentration | Icon | Meaning |
|--------|-------|----------------|------|---------|
| OUTBREAK | 🔴 Red | ≥40% | ⚠️ | High alert - immediate action needed |
| MONITOR | 🟡 Yellow | 20-39% | ⚠️ | Watch closely - potential escalation |
| OK | 🟢 Green | <20% | ✓ | Normal - keep monitoring |
| NO DATA | ⚫ Gray | 0% | ○ | No cases reported |

## API Endpoints Used

The frontend communicates with these backend endpoints:

### 1. GET /ping
```
Checks if backend is running
Response: {"message": "Pong"}
```

### 2. POST /simulate-batch?size=50&mode=obvious
```
Generate obvious disease patterns
Query Parameters:
  - size: number of cases (5-500, default 50)
  - mode: "obvious" or "random"

Response: {
  "status": "success",
  "cases_generated": 50,
  "data_type": "Clear disease patterns (HIGH SIGNAL)",
  "note": "Each disease has distinctive symptoms"
}
```

### 3. POST /simulate-batch?size=50&mode=random
```
Generate random symptom patterns
Query Parameters: Same as obvious mode
Response: Same as obvious mode, different data_type
```

### 4. POST /predict
```
Run disease prediction and outbreak detection
Request Body: None (uses batch_data.csv from last simulation)

Response: {
  "timestamp": "2024-03-28T14:30:45",
  "model": "Random Forest (6-class Disease Classifier)",
  "explainability": "SHAP-inspired Feature Importance",
  "total_analyzed": 50,
  "nationwide": {
    "malaria": {
      "cases": 30,
      "status": "OUTBREAK",
      "key_features": ["fever", "chills", "body_pain"]
    },
    ...
  },
  "regions": [
    {
      "region": "Machakos",
      "total_cases": 20,
      "diseases": {"malaria": 12, "flu": 8},
      "concentration": 60.0,
      "status": "OUTBREAK",
      "key_features": ["fever", "chills", "body_pain"]
    },
    ...
  ]
}
```

## JavaScript Functions

### API Interactions
- `checkApiHealth()` - Ping backend for health status
- `simulateObvious()` - Generate obvious pattern data
- `simulateRandom()` - Generate random pattern data
- `runPrediction()` - Run disease predictions

### Display Functions
- `displayPredictionResults(data)` - Render prediction results
- `createRegionCard(region)` - Create region status cards
- `updateHealthStatus(isHealthy, message)` - Update header status

### Helper Functions
- `formatDiseaseName(disease)` - Format disease names for display
- `showError(message)` - Display error messages

## Customization

### Change Color Scheme
Edit the `statusColors` object in `app.js`:
```javascript
const statusColors = {
    'OUTBREAK': { bg: 'bg-red-900', border: 'border-red-500', ... },
    // Change colors here
};
```

### Adjust API URL
Change `API_BASE_URL` in `app.js`:
```javascript
const API_BASE_URL = 'http://your-backend-url:8000';
```

### Modify Status Thresholds
Edit concentration thresholds in `app.js`:
```javascript
// Lines ~91-98
if (pct >= 50) {  // Change 40 to your threshold
    status = 'OUTBREAK';
}
```

## Browser Compatibility
- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- IE11: ❌ Not supported (uses modern CSS/JS)

## Performance Tips
1. Use "Obvious" mode for presentations (faster, clearer)
2. Use "Random" mode for stress testing (test model robustness)
3. Generate 50-100 cases for quick feedback
4. Generate 500 cases for comprehensive analysis

## Troubleshooting

### API Connection Error
**Problem**: "Connection Error: Failed to fetch"
**Solution**:
1. Ensure backend is running: `uvicorn app.main:app --reload`
2. Check backend is on `http://localhost:8000`
3. Verify CORS is enabled in `backend/app/main.py`

### No Batch Data Error
**Problem**: "error: No batch data found"
**Solution**:
1. Click "GENERATE" on Obvious or Random Patterns card first
2. Wait for success confirmation
3. Then click "RUN PREDICTION"

### Model Not Found Error
**Problem**: "error: Model not found"
**Solution**:
1. Train the model: `python backend/app/models/train.py`
2. Ensure `backend/app/models/model.pkl` exists
3. Restart backend server

## Future Enhancements
- [ ] Real-time data streaming
- [ ] Chart.js visualizations for disease trends
- [ ] Time-series analysis
- [ ] Export reports as PDF
- [ ] Dark/Light theme toggle
- [ ] Mobile responsive optimization (already responsive, just needs testing)
- [ ] Multi-region comparison charts

## Support & Issues
For issues or suggestions, check:
1. Browser console (F12) for JavaScript errors
2. Backend logs for API errors
3. Ensure all dependencies are installed
4. Check file paths and permissions

---

**Version**: 1.0.0  
**Last Updated**: March 2024  
**Built with**: Tailwind CSS, Vanilla JS, Font Awesome Icons
