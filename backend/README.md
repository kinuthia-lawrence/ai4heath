# Python Environment Setup & Project Run Guide

## 1. Check if Python is Installed

Open a terminal and run:

```bash
python --version
```

You should see output like `Python 3.8.10` or higher. If not, download and install Python from [python.org](https://www.python.org/downloads/).

## 2. Create and Activate a Virtual Environment (Recommended)

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

## 3. Install Project Dependencies

```bash
pip install -r requirements.txt
```

## 4. Run the FastAPI App

```bash
uvicorn app.main:app --reload
```

Visit http://127.0.0.1:8000/docs for the interactive API documentation.

# AI4Health: Outbreak Prediction & Analytics Backend

## Overview

This project provides a backend system for automated disease outbreak prediction and explainable analytics using health data. It is designed for batch processing (via clone jobs), with a frontend UI that pulls analytics results for display.

## Features

- Batch ingestion of simulated or real health data (CSV, JSON, DB)
- Data preprocessing and feature engineering
- Model training, loading, inference, and periodic retraining
- Automated prediction and explainability (SHAP/LIME)
- Results storage and monitoring
- API endpoints for frontend analytics display

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── utils/
│   │   ├── data_loader.py
│   │   ├── utils.py
│   │   ├── feature_engineering.py
│   │   └── monitor.py
│   ├── models/
│   │   └── model.py
│   ├── services/
│   │   ├── explain.py
│   │   └── predict.py
│   ├── storage/
│   │   ├── results_store.py
│   │   └── model_store.py
│   ├── api/
│   │   └── endpoints.py
│   ├── jobs/
│   │   └── clone_job.py
│   └── schemas/
│       └── schema.py
├── requirements.txt
├── README.md
└── data/
```

## Flow

- Data is simulated/imported and ingested.
- Preprocessing and feature engineering are applied.
- Model is trained (if not already) and saved.
- Clone jobs trigger batch predictions and explainability.
- Results are stored and monitored.
- Frontend UI pulls analytics results via API.

## Usage

1. Place your health data in the `data/` folder.
2. Configure and run the backend (see `main.py`).
3. Schedule or trigger clone jobs for batch prediction.
4. Access analytics results from the API for frontend display.

## Requirements

- Python 3.8+
- See `requirements.txt` for dependencies.

## License

MIT
