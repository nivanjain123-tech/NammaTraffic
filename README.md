# NammaTraffic — Bengaluru Traffic Incident Intelligence & Command Platform

> **Flipkart Gridlock Hackathon 2.0** | Theme: Event-Driven Congestion (Planned & Unplanned)

**NammaTraffic** transforms Bengaluru's reactive traffic incident handling into a **proactive command platform**. It predicts incident severity, estimates road closure probability, forecasts resolution time, recommends resource allocation and diversion routes, and provides an AI Copilot for traffic operations — all powered by **8,173 real Astram incident records**.

---

## 🚀 Quick Start

### 1. Activate Environment & Install Dependencies
```bash
source /path/to/your/venv/bin/activate
pip install streamlit folium streamlit-folium plotly pandas numpy scikit-learn catboost lightgbm
```

### 2. Train ML Models (one-time, ~2 min)
```bash
cd Gridlock_Round2/code
python train_pipeline.py
```
Generates trained models, similarity matrix, hotspot clusters, and corridor risk scores in `artifacts/`.

### 3. Run the Command Center
```bash
cd Gridlock_Round2/code
streamlit run app.py
```
Open **http://localhost:8501** in your browser.

---

## 🎯 Demo Script (2 Minutes for Judges)

1. **Operations Dashboard** — Show live critical incident feed, KPIs, and post-event analytics (fastest police stations, 3-month trend).
2. **GIS Risk Map** — Toggle time-lapse slider to 18:00, enable High-Risk Corridors, show hotspot clusters.
3. **Incident Predictor** — Click **"Scenario 1: Severe Accident — Silk Board (6 PM)"** → hit Predict → show ML predictions, SHAP-like explanation, and diversion routes.
4. **AI Copilot** — Ask *"Show me a chart of incidents by cause"* or *"Which police station resolves incidents fastest?"*

---

## 📁 Folder Structure

```
Gridlock_Round2/
├── selected_theme/          # Astram event dataset (8,173 incidents)
├── code/
│   ├── train_pipeline.py    # ML training + feature engineering
│   ├── app.py               # Streamlit command center UI
│   └── data_audit.py        # Dataset analysis script
├── artifacts/               # Trained models, matrices, stats
├── reports/                 # 22 architecture & analysis docs
├── handover_bundle/         # Self-contained project package
└── README.md
```

---

## 🧠 Platform Capabilities

| Module | Capability |
|---|---|
| 📊 Operations Dashboard | Live critical feed, KPIs, cause/hour charts, corridor risk ranking, post-event analytics |
| 🗺️ GIS Risk Map | Heatmap, markers, DBSCAN hotspots, time-lapse hour slider, high-risk corridor polylines |
| 🔍 Incident Explorer | Filter/search + cosine-similarity retrieval of past incidents |
| 🧠 AI Traffic Copilot | Rule-based Q&A + optional OpenAI/Gemini LLM, chat history, inline charts |
| 📈 ML Performance | 3 models with 5-fold CV metrics |
| 🔮 Incident Predictor | ML predictions, SHAP-like explanations, diversion routes, demo scenarios |

---

## 🤖 ML Models

| Model | Target | Algorithm | Performance |
|---|---|---|---|
| Severity | Priority (High/Low) | CatBoost | F1 = 0.999 |
| Road Closure | requires_road_closure | LightGBM | AUC = 0.796 |
| Resolution Time | Minutes to resolve | CatBoost | MAE ≈ 2200 min |

---

## 📊 Dataset

**Astram Event Data** — 8,173 real Bengaluru traffic incidents (Nov 2023 – Apr 2024)
- 94.3% unplanned, 5.7% planned events
- 17 event causes (vehicle_breakdown 60%, accident 4.5%, tree_fall 3.5%…)
- 22 corridors, 54 police stations
- GPS coordinates, resolution times, road closure flags

---

## 💡 Why NammaTraffic Wins

- **Proactive, not reactive** — Predict closure probability *before* dispatching resources
- **Real data, real models** — Trained on 8K+ Bengaluru incidents, not synthetic data
- **Operations-ready UX** — Dark command-center theme built for traffic control rooms
- **Explainable AI** — Every prediction comes with human-readable reasoning
- **Diversion intelligence** — Automatic alternate route suggestions when closure risk > 30%

Built with ❤️ for Bengaluru. **Namma Raste, Namma Jaaga.**
