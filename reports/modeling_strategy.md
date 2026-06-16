# Modeling Strategy — Phase 8
## Prediction Tasks for Bengaluru Traffic Incident Intelligence Platform

Based on the Astram event dataset (8,204 incidents), we identify **5 core prediction tasks** that are directly derivable from the data and immediately useful in the product.

---

## Task 1: Severity / Priority Classification

| Attribute | Detail |
|---|---|
| **Target** | `priority` — High (61.5%) / Low (38.4%) — binary classification (only 2 values exist + 2 nulls) |
| **Features** | `event_type`, `event_cause`, `latitude`, `longitude`, `hour_of_day`, `day_of_week`, `corridor`, `zone`, `requires_road_closure`, `veh_type`, local incident density (count of incidents within 1km in last 24h) |
| **Evaluation** | Macro F1-Score, Confusion Matrix |
| **Baseline** | Most-frequent class (~55% accuracy if High is dominant) |
| **Best Model** | CatBoost Classifier with native categoricals |
| **UI Usage** | Automatic severity badge on new incidents; risk-colored markers on map |
| **Why it matters** | Operators can instantly triage — High-priority incidents get immediate resource dispatch |

---

## Task 2: Road Closure Prediction

| Attribute | Detail |
|---|---|
| **Target** | `requires_road_closure` — TRUE / FALSE (binary classification) |
| **Features** | `event_cause`, `event_type`, `priority`, `latitude`, `longitude`, `corridor`, `hour_of_day`, `veh_type`, description text features (TF-IDF top 50) |
| **Evaluation** | ROC-AUC, Precision-Recall (important: closure = minority class) |
| **Baseline** | Class ratio baseline (~15% closure rate estimated) |
| **Best Model** | LightGBM with class weight balancing |
| **UI Usage** | Road closure probability gauge on incident card; pre-emptive diversion trigger |
| **Why it matters** | Road closures cause cascading congestion — early prediction enables proactive response |

---

## Task 3: Resolution Time Prediction

| Attribute | Detail |
|---|---|
| **Target** | `resolution_minutes` = `resolved_datetime - start_datetime` (regression, minutes) |
| **Features** | `event_cause`, `event_type`, `priority`, `requires_road_closure`, `latitude`, `longitude`, `corridor`, `hour_of_day`, `day_of_week`, `zone`, `police_station` |
| **Evaluation** | MAE (Mean Absolute Error in minutes), RMSE, R² |
| **Baseline** | Global median resolution time |
| **Best Model** | CatBoost Regressor; consider survival analysis (Kaplan-Meier) for censored observations where `resolved_datetime` is NULL |
| **UI Usage** | "Estimated resolution: ~45 minutes" on incident card; timeline visualization |
| **Why it matters** | Operators can set expectations, plan shift changes, and communicate ETAs to public |

---

## Task 4: Event Cause Classification

| Attribute | Detail |
|---|---|
| **Target** | `event_cause` — vehicle_breakdown / accident / tree_fall / road_work / protest / others (multi-class) |
| **Features** | `latitude`, `longitude`, `hour_of_day`, `day_of_week`, `corridor`, `zone`, `veh_type`, `description` (NLP features) |
| **Evaluation** | Macro F1-Score |
| **Baseline** | Most-frequent class |
| **Best Model** | CatBoost with TF-IDF description features |
| **UI Usage** | Auto-classification of incoming incident reports; reduces manual categorization |
| **Why it matters** | Speeds up incident intake; enables automatic routing to correct response team |

---

## Task 5: Resource Requirement Estimation

| Attribute | Detail |
|---|---|
| **Target** | Derived: `resource_level` based on priority × road_closure × event_cause → Low (1 officer) / Medium (2-3 officers + barricades) / High (5+ officers + tow truck + barricades) |
| **Features** | All incident features + predicted severity + predicted road closure probability |
| **Evaluation** | Ordinal accuracy, MAE on resource count |
| **Baseline** | Rule-based mapping from priority |
| **Best Model** | Hybrid: ML prediction for severity/closure → rule-based resource mapping |
| **UI Usage** | Resource recommendation card: "Deploy 3 officers, 4 barricades, 1 tow truck" |
| **Why it matters** | Eliminates guesswork in resource deployment; prevents over/under-allocation |

---

## Modeling Pipeline Architecture

```
Raw Incident → Feature Engineering → [Parallel Predictions]
                                      ├─ Task 1: Severity (CatBoost)
                                      ├─ Task 2: Road Closure (LightGBM)
                                      ├─ Task 3: Resolution Time (CatBoost)
                                      ├─ Task 4: Event Cause (CatBoost + NLP)
                                      └─ Task 5: Resource Needs (Hybrid)
                                                    ↓
                                          Enriched Incident Card
                                                    ↓
                                          → UI Display
                                          → Copilot Context
                                          → Alert System
```

## Feature Engineering Plan

| Feature Group | Features | Source |
|---|---|---|
| **Spatial** | lat, lon, geohash, corridor_encoded, zone_encoded, nearest_junction_distance | lat/long columns |
| **Temporal** | hour, minute, day_of_week, is_weekend, is_peak_hour, month | start_datetime |
| **Categorical** | event_type, event_cause, veh_type, corridor, zone, police_station | Direct columns |
| **Text** | TF-IDF top 50 from description, keyword flags (breakdown, accident, fire, protest) | description column |
| **Density** | incident_count_1km_24h, incident_count_corridor_7d, closure_rate_corridor | Historical aggregation |
| **Interaction** | cause×corridor, cause×hour, zone×hour | Feature crosses |

## Validation Strategy

- **Primary**: Stratified 5-Fold CV (stratified on priority)
- **Secondary**: Temporal split (train on months 1-4, validate on month 5)
- **Metric alignment**: Use the same metric that would be used in real operations (F1 for classification, MAE for regression)
