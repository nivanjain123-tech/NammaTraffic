# ML Architecture — Bengaluru Traffic Incident Intelligence Platform

## Overview

The ML layer provides 5 prediction services that enrich every incoming incident with actionable intelligence. All models are lightweight, interpretable gradient-boosted trees optimized for sub-100ms inference.

```
┌─────────────────────────────────────────────────────────┐
│                   ML Prediction Pipeline                 │
│                                                         │
│  Raw Incident ──→ Feature Engine ──→ ┌─ Severity       │
│                                      ├─ Road Closure    │
│                                      ├─ Resolution Time │
│                                      ├─ Event Cause     │
│                                      └─ Resource Needs  │
│                                              ↓          │
│                                    Enriched Incident     │
│                                              ↓          │
│                                    ┌─ API Response      │
│                                    ├─ Copilot Context   │
│                                    └─ Alert Trigger     │
└─────────────────────────────────────────────────────────┘
```

---

## Model 1: Priority / Severity Classifier

| Spec | Detail |
|---|---|
| **Type** | Binary Classification |
| **Target** | `priority` — High (61.5%) vs Low (38.4%) |
| **Algorithm** | CatBoost Classifier |
| **Features** | event_cause, event_type, corridor, zone, hour, day_of_week, lat, lon, requires_road_closure, veh_type |
| **Eval Metric** | F1-Score (macro), ROC-AUC |
| **Baseline** | Majority class = 61.5% accuracy |
| **Expected** | ~82-88% F1 |
| **Serving** | REST API, <50ms latency |

### CatBoost Config
```python
from catboost import CatBoostClassifier

model = CatBoostClassifier(
    iterations=1500,
    learning_rate=0.05,
    depth=6,
    loss_function='Logloss',
    cat_features=['event_cause', 'event_type', 'corridor', 'zone', 'veh_type'],
    random_seed=42,
    verbose=100,
    early_stopping_rounds=100
)
```

---

## Model 2: Road Closure Predictor

| Spec | Detail |
|---|---|
| **Type** | Binary Classification (imbalanced) |
| **Target** | `requires_road_closure` — FALSE (91.7%) vs TRUE (8.3%) |
| **Algorithm** | LightGBM with scale_pos_weight |
| **Key Signal** | event_cause is the #1 predictor: VIP movement (80% closure), public_event (46.4%), protest (40%), tree_fall (39.4%), construction (26.5%) |
| **Eval Metric** | PR-AUC, F1 on positive class |
| **Expected** | ~75-85% PR-AUC |

### Handling Imbalance
```python
import lightgbm as lgb

params = {
    'objective': 'binary',
    'metric': 'average_precision',
    'scale_pos_weight': 91.7 / 8.3,  # ~11x
    'learning_rate': 0.03,
    'max_depth': 5,
    'num_leaves': 31,
}
```

---

## Model 3: Resolution Time Regressor

| Spec | Detail |
|---|---|
| **Type** | Regression (log-transformed) |
| **Target** | `resolution_minutes` = resolved_datetime - start_datetime |
| **Records** | 3,192 usable (39.1% of dataset) |
| **Distribution** | Median: 1.1h, Mean: 103.8h, heavily right-skewed |
| **Algorithm** | CatBoost Regressor on log(minutes + 1) |
| **Eval Metric** | MAE (minutes), RMSE, R² |

### Binned Classification Alternative
For the UI, we also train a classifier on resolution time bins:

| Bin | Label | Count | % |
|---|---|---|---|
| <30min | Quick | 849 | 26.6% |
| 30min-2h | Moderate | 1,331 | 41.7% |
| 2h-12h | Extended | 268 | 8.4% |
| 12h-24h | Long | 76 | 2.4% |
| >24h | Critical | 668 | 20.9% |

---

## Model 4: Event Cause Classifier

| Spec | Detail |
|---|---|
| **Type** | Multi-class (17 classes, but top 7 cover 95%) |
| **Target** | `event_cause` |
| **Algorithm** | CatBoost with TF-IDF on description |
| **Key Features** | lat/lon (location signal), hour, corridor, veh_type, description keywords |

### NLP Feature Extraction
```python
from sklearn.feature_extraction.text import TfidfVectorizer

# Extract keywords from description (mixed English/Kannada)
tfidf = TfidfVectorizer(max_features=100, stop_words='english')
desc_features = tfidf.fit_transform(train['description'].fillna(''))
```

---

## Model 5: Resource Estimator (Hybrid)

| Spec | Detail |
|---|---|
| **Type** | Hybrid: ML prediction → Rule-based mapping |
| **Output** | officers_needed, barricades_needed, tow_truck_needed |

### Rule Engine (post-ML)
```python
def estimate_resources(severity, road_closure_prob, event_cause):
    resources = {'officers': 1, 'barricades': 0, 'tow_truck': False}
    
    if severity == 'High':
        resources['officers'] = 3
    if road_closure_prob > 0.5:
        resources['barricades'] = 4
        resources['officers'] += 2
    if event_cause == 'vehicle_breakdown':
        resources['tow_truck'] = True
    if event_cause in ['protest', 'public_event', 'vip_movement']:
        resources['officers'] += 3
        resources['barricades'] += 6
    
    return resources
```

---

## Similar Incident Search (Non-ML Module)

### Approach: Cosine Similarity on Multi-Modal Embeddings

```
Incident Vector = [
    one_hot(event_cause),      # 17 dims
    one_hot(corridor),          # 22 dims
    normalized(lat, lon),       # 2 dims
    normalized(hour),           # 1 dim
    tfidf(description)          # 50 dims
]                               # Total: ~92 dims
```

### Search Algorithm
```python
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def find_similar(new_incident_vector, historical_matrix, top_k=5):
    similarities = cosine_similarity(
        new_incident_vector.reshape(1, -1), 
        historical_matrix
    )[0]
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    return top_indices, similarities[top_indices]
```

---

## Training Pipeline

```
1. Load Astram CSV
2. Clean: drop 100% null cols, fill categoricals, parse datetimes
3. Engineer: hour, day_of_week, geohash, incident_density, tfidf
4. Split: Stratified 5-Fold CV (stratified on priority)
5. Train: CatBoost/LightGBM per task
6. Evaluate: F1, AUC, MAE per fold
7. Serialize: Save models as .cbm / .lgb files
8. Index: Build FAISS index for similar-incident search
9. Serve: Load models in FastAPI at startup
```

## Model Serving Architecture

```
FastAPI App Startup
    ├── Load severity_model.cbm
    ├── Load closure_model.lgb
    ├── Load resolution_model.cbm
    ├── Load cause_model.cbm
    ├── Load tfidf_vectorizer.pkl
    ├── Load similarity_matrix.npy
    └── Load faiss_index.bin

POST /api/predict
    → Feature extraction (5ms)
    → Parallel model inference (20ms each)
    → Resource rule engine (1ms)
    → Similarity search (10ms)
    → Return enriched incident (total <100ms)
```
