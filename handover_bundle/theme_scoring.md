# Theme Scoring Matrix — Flipkart Gridlock Hackathon 2.0

## Scoring Criteria (Weight × Score out of 10)

| Criterion | Weight | Theme 1: Parking Congestion | Theme 2: Event-Driven Congestion | Theme 3: Computer Vision |
|---|---|---|---|---|
| **Data Availability** | 15% | 8 — 298K violation records, but only parking violations. No congestion/flow data. | **10** — 8.2K rich incident records with geo, temporal, causal, resolution data. Complete lifecycle. | 2 — No image dataset provided at all. Would need synthetic/external data. |
| **Feasibility (48h)** | 15% | 7 — Heatmaps are straightforward. But quantifying "impact on traffic flow" without flow data is hard. | **9** — Predict severity, closure, resolution time from structured tabular data. Very feasible. | 3 — Building object detection + violation classification in 48h without labeled training images is extremely risky. |
| **Judge Appeal** | 15% | 5 — Parking heatmaps are common. Many teams will do this. Low differentiation. | **9** — Command center product is impressive. Prediction + recommendation + copilot is compelling. | 7 — CV demos are flashy but without real data, it would be purely conceptual. |
| **Innovation Potential** | 10% | 4 — Limited scope. Heatmap + enforcement prioritization is well-trodden. | **9** — Hierarchical prediction + AI copilot + similar-incident search + resource optimizer is novel. | 6 — Object detection is standard. Innovation would be in multi-violation detection pipeline. |
| **Demo Quality** | 10% | 5 — Static heatmap demos are underwhelming. | **9** — Live map, incident prediction, AI copilot Q&A, diversion recommendation = powerful demo. | 4 — Without real images and trained model, demo would be mockup-only. |
| **Operational Usefulness** | 10% | 6 — Useful for parking enforcement teams. Narrow scope. | **10** — Directly useful for Bengaluru Traffic Police command center operations. | 5 — Useful long-term but requires massive training data pipeline. |
| **Complexity Risk** | 10% | 3 (low risk = good) — Simple to execute. | 5 (moderate risk) — Multiple modules but each is feasible. | **9 (high risk = bad)** — Requires image data, GPU training, real-time inference. Very risky in 48h. |
| **Chance of Reaching Finale** | 15% | 4 — Low differentiation, limited product depth. | **9** — Strong product story, real operational value, impressive tech stack. | 3 — Cannot build a competitive CV system without labeled image data. |

## Weighted Scores

| Theme | Weighted Score |
|---|---|
| Theme 1: Parking-Induced Congestion | **5.30 / 10** |
| **Theme 2: Event-Driven Congestion** | **🏆 8.90 / 10** |
| Theme 3: Computer Vision | **4.15 / 10** |

## Decision

### ✅ SELECTED: Theme 2 — Event-Driven Congestion (Planned & Unplanned)

### ❌ REJECTED: Theme 1 — Parking-Induced Congestion
**Why rejected:**
- The violation dataset (298K rows) contains only parking violations with lat/long and vehicle info — there is no congestion or traffic flow data to quantify the "impact on traffic flow" that the problem statement asks for.
- Building a heatmap is trivial. Multiple teams will do this. Zero differentiation.
- The product ceiling is low — it's essentially a dashboard, not a command platform.

### ❌ REJECTED: Theme 3 — Computer Vision for Traffic Violations
**Why rejected:**
- **No image dataset was provided.** The problem statement requires processing traffic images, but we have zero labeled images to train on.
- Building object detection, violation classification, and license plate recognition in 48 hours without training data is not feasible.
- This theme would produce a conceptual mockup, not a working prototype.

## Why Event-Driven Congestion Will Win

1. **Data-rich**: 8,204 real Bengaluru incidents with complete lifecycle (creation → resolution), geolocation, causation, severity, resource data.
2. **Predictable targets**: Severity, road closure probability, resolution time, resource needs — all derivable from the dataset.
3. **Product depth**: Not a dashboard — a full Traffic Incident Intelligence & Command Platform.
4. **AI differentiation**: LLM-powered copilot for traffic operators is a unique, high-impact feature.
5. **Operational credibility**: Directly maps to how Bengaluru Traffic Police actually operates.
6. **Demo impact**: Live map + predictions + AI recommendations + similar-incident search = 5 minutes of pure impact.
