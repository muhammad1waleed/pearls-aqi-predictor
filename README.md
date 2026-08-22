# 🌫️ Pearls AQI Predictor

A serverless, end-to-end machine learning system that forecasts Air Quality Index (AQI) for Rawalpindi, Pakistan, 1–3 days in advance. Built as a complete MLOps pipeline: automated data collection, feature engineering, model training with experiment comparison, a versioned model registry, and a live public dashboard with explainable predictions.

**🔗 Live dashboard:** _[https://pearls-aqi-predict.streamlit.app/]_

---

## What this project does

- Collects live weather and air pollution data for Rawalpindi every hour
- Engineers time-based and historical (lag/rolling) features
- Trains and compares multiple ML models (Ridge Regression vs. Random Forest) per forecast horizon
- Automatically retrains and re-registers models daily on fresh data
- Serves 1-day, 2-day, and 3-day AQI forecasts through a public Streamlit dashboard
- Explains every prediction using SHAP (SHapley Additive exPlanations)
- Alerts when forecasted AQI crosses into hazardous territory

## Why this project matters

Most AQI apps show current air quality. This project instead predicts *where AQI is heading*, so someone can plan ahead — e.g., knowing tomorrow will be worse than today, before it happens. It also demonstrates a complete, realistic MLOps workflow: not just a Jupyter notebook with a trained model, but a system that collects its own data, retrains itself, and stays live without manual intervention.

---

## Architecture

```
OpenWeather API (weather + pollution)
        ↓
Feature Pipeline (hourly, GitHub Actions)
   - fetch → engineer (time + lag/rolling features) → validate
        ↓
Hopsworks Feature Store (versioned, queryable)
        ↓
Training Pipeline (daily, GitHub Actions)
   - build training set → train Ridge + Random Forest per target
   - compare on time-based train/test split → select best model per horizon
   - compute SHAP feature importance → register winning models
        ↓
Hopsworks Model Registry (versioned models)
        ↓
Streamlit Dashboard (public, live)
   - load latest models → fetch latest features → predict
   - explain via SHAP → alert if hazardous
```

## Tech stack

| Layer | Technology | Why |
|---|---|---|
| Data source | OpenWeather API | Free tier, weather + pollution in one ecosystem |
| Feature store | Hopsworks (Hudi format) | Purpose-built for ML feature versioning and point-in-time correctness |
| Modeling | scikit-learn (Ridge, Random Forest) | Right-sized for tabular forecasting; supports rigorous baseline comparison |
| Explainability | SHAP | Per-prediction and global feature importance |
| Model registry | Hopsworks Model Registry | Versioned, queryable model storage |
| Automation | GitHub Actions | Free scheduled compute, no infrastructure to manage |
| Dashboard | Streamlit (Community Cloud) | Fast to build, free to host, purpose-built for data apps |
| Testing | pytest | 17 unit tests covering feature logic, edge cases, error handling |

## Model results

Three independent models forecast AQI at three horizons. Each was trained on ~8,400 hourly readings spanning a full year (Aug 2025–Aug 2026), compared against a Ridge Regression baseline, and selected based on held-out test performance using a **time-respecting** train/test split (no data leakage from shuffling).

| Horizon | Model | RMSE | MAE | R² |
|---|---|---|---|---|
| 1 day | Random Forest | 0.625 | 0.470 | 0.273 |
| 2 days | Ridge Regression | 0.707 | 0.545 | 0.087 |
| 3 days | Ridge Regression | 0.718 | 0.559 | 0.053 |

**Key finding:** Random Forest outperforms Ridge at the 1-day horizon (where a strong, learnable signal exists — current AQI is highly predictive of tomorrow's AQI), but *underperforms* Ridge at 2–3 days out, where the true signal is weaker and Random Forest's flexibility leads to overfitting rather than genuine predictive power. This was discovered empirically through systematic comparison, not assumed — a good illustration that "more powerful model" and "more accurate model" are not the same thing.

SHAP analysis shows the same pattern: `aqi` (the current reading) dominates the 1-day prediction, while pollutant composition (`pm10`, `pm2_5`, `co`) becomes more influential at longer horizons — current AQI is a strong short-term signal but a weak long-term one.

## Project structure

```
pearls-aqi-predictor/
├── feature_pipeline/          # Fetch, engineer, store features
├── training_pipeline/         # Train, compare, explain, register models
├── dashboard/                  # Streamlit app (predictions, SHAP, alerts)
├── tests/                      # pytest unit tests
├── notebooks/                  # Throwaway exploration/verification scripts
├── .github/workflows/          # Hourly feature pipeline + daily training pipeline
├── requirements.txt             # Full dependencies (dashboard + pipelines)
├── requirements-pipeline.txt   # Pipeline-only dependencies (excludes Streamlit)
├── SECURITY.md                  # Security review notes and known limitations
└── runtime.txt                  # Pins Python version for Streamlit Cloud
```

## Running locally

**1. Clone and set up environment**
```bash
git clone https://github.com/muhammad1waleed/pearls-aqi-predictor.git
cd pearls-aqi-predictor
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

**2. Configure secrets**

Copy `.env.example` to `.env` and fill in your own keys:
```
OPENWEATHER_API_KEY=your_key_here
HOPSWORKS_API_KEY=your_key_here
```

**3. Run the feature pipeline once** (populates the feature store)
```bash
python -m feature_pipeline.run
```

**4. Train and register models**
```bash
python -m training_pipeline.save_to_registry
```

**5. Launch the dashboard**
```bash
streamlit run dashboard/app.py
```

**6. Run tests**
```bash
pytest tests/ -v
```

## Automation

Two GitHub Actions workflows run independently of any local machine:
- **Hourly Feature Pipeline** (`.github/workflows/feature_pipeline.yml`) — fetches live data every hour
- **Daily Training Pipeline** (`.github/workflows/training_pipeline.yml`) — retrains and re-registers all 3 models daily

Both require `OPENWEATHER_API_KEY` and `HOPSWORKS_API_KEY` as GitHub Actions repository secrets.

## Security

See [SECURITY.md](SECURITY.md) for details on secrets handling, dependency vulnerability review, and API key scope minimization.

## Author

Muhammad Waleed — built as part of the 10Pearls Shine Internship Program (Data Sciences track).