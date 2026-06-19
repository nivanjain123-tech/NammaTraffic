# NammaTraffic

**Flipkart Gridlock Hackathon 2.0**
Theme: Event-Driven Congestion (Planned & Unplanned)

NammaTraffic is a predictive command platform designed to shift Bengaluru's traffic incident management from a reactive approach to a proactive one. Built using 8,173 real Astram incident records, the system forecasts incident severity, estimates road closure probability, predicts resolution times, and suggests resource allocations and diversions. We have also integrated an AI Copilot to help traffic operations personnel query data naturally.

---

## Quick Start

### 1. Setup Environment
```bash
source /path/to/your/venv/bin/activate
pip install -r requirements.txt
```

### 2. Train the Models
```bash
cd code
python train_pipeline.py
```
This script takes about 2 minutes to run. It generates the trained models, similarity matrix, hotspot clusters, and corridor risk scores, saving them all in the `artifacts/` directory.

### 3. Start the Command Center
```bash
cd code
streamlit run app.py
```
The dashboard will be available at http://localhost:8501.

---

## Demo Walkthrough

If you are evaluating the project, here is a quick way to test the core features:

1. **Operations Dashboard:** Check the live incident feed, KPI metrics, and post-event analytics to see trends and station performance.
2. **GIS Risk Map:** Use the time-lapse slider (try setting it to 18:00), turn on High-Risk Corridors, and view the spatial hotspot clusters.
3. **Incident Predictor:** Select "Scenario 1: Severe Accident — Silk Board (6 PM)" and click Predict. You will see the model's predictions, the reasoning behind them, and suggested diversion routes.
4. **AI Copilot:** Navigate to the Copilot section and ask questions like "Show me a chart of incidents by cause" or "Which police station resolves incidents fastest?".

---

## Folder Structure

```
Gridlock_Round2/
├── code/
│   ├── train_pipeline.py    # ML training and feature engineering
│   ├── app.py               # Streamlit UI
├── artifacts/               # Saved models, matrices, and stats (generated after training)
├── NAMMATRAFFIC_PITCHDECK.pptx
├── NAMMATRAFFIC_PITCHDECK.key
└── README.md
```

*(Note: We have removed the heavy raw data files from the repository to keep the submission clean and within size limits. The models run inference directly from the generated artifacts.)*

---

## Core Capabilities

- **Dashboard:** Live feeds, KPIs, hourly breakdown charts, and corridor risk rankings.
- **GIS Mapping:** Density heatmaps, DBSCAN hotspot clustering, and time-based filtering.
- **Search:** Retrieve past incidents using cosine-similarity based on event parameters.
- **Traffic Copilot:** Rule-based Q&A that can dynamically render charts or answer operational queries.
- **Predictor:** Runs CatBoost and LightGBM models to predict resolution times and severity, complete with SHAP-like explanations and diversion logic.

---

## Machine Learning Models

We built three primary models evaluated using 5-fold cross validation:
- **Severity Prediction:** Classifies events into High/Low priority using CatBoost. (F1 = 0.999)
- **Road Closure Prediction:** Estimates the probability that a road will require complete closure using LightGBM. (AUC = 0.796)
- **Resolution Time:** Predicts the total minutes required to resolve an incident using CatBoost. Our optimized model achieved an MAE of ~2.2 hours.

---

## The Dataset

The system was trained on Astram Event Data, comprising 8,173 real Bengaluru traffic incidents recorded between November 2023 and April 2024.
- 94.3% of events were unplanned, 5.7% were planned.
- Covered 17 event causes (mostly vehicle breakdowns, accidents, and tree falls).
- Mapped across 22 corridors and 54 police stations.

---

## Why We Built This

Current traffic systems tell you there is a jam after it happens. We built NammaTraffic to calculate the risk of closure before the first tow truck is even dispatched. By training entirely on real Bengaluru operational data rather than synthetic datasets, we've developed a system that is genuinely ready for deployment in a traffic control room.

Built for Bengaluru. Namma Raste, Namma Jaaga.
