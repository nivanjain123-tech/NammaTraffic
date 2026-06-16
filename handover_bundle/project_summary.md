# Project Summary

## Bengaluru Traffic Incident Intelligence & Command Platform
### Flipkart Gridlock Hackathon 2.0 — Round 2

---

## One-Line Summary

An AI-powered command platform that transforms Bengaluru's reactive traffic incident response into a predictive, data-driven operation — forecasting severity, recommending resources, suggesting diversions, and learning from every past incident.

## Theme

**Event-Driven Congestion (Planned & Unplanned)** — Selected after scoring 8.90/10 against two alternatives (Parking: 5.30, CV: 4.15).

## Dataset

**Astram Event Data** — 8,204 real traffic incidents from Bengaluru with:
- Full incident lifecycle (creation → assignment → resolution → closure)
- Geolocation (lat/long for start and end points)
- Causation taxonomy (vehicle_breakdown, accident, tree_fall, road_work, protest, etc.)
- Temporal data (start/end/created/modified/resolved/closed timestamps)
- Organizational data (police_station, zone, corridor, junction)
- Severity metadata (priority, road_closure flag)

## Product Architecture

8 integrated modules:
1. **Incident Intelligence Engine** — Enrich incoming incidents with predictions and context
2. **Congestion Forecasting Engine** — Predict severity and impact before it happens
3. **Resource Allocation Recommender** — Data-backed officer/barricade/tow-truck recommendations
4. **Diversion Recommendation Engine** — Instant alternative route suggestions
5. **Similar Incident Search** — "This happened before — here's how we solved it"
6. **GIS Hotspot & Risk Map** — Spatial intelligence layer
7. **AI Traffic Copilot** — Natural language interface for operators
8. **Post-Event Learning Engine** — Continuous improvement from closed incidents

## ML Tasks

| Task | Type | Target | Primary Model |
|---|---|---|---|
| Severity Prediction | Classification | priority (H/M/L) | CatBoost |
| Road Closure Prediction | Binary Classification | requires_road_closure | LightGBM |
| Resolution Time | Regression | minutes to resolve | CatBoost |
| Event Cause Classification | Multi-class | event_cause | CatBoost + NLP |
| Resource Estimation | Hybrid | resource_level | ML + Rules |

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, React, MapLibre GL JS, Recharts, Shadcn/ui |
| Backend | FastAPI (Python), Pydantic, SQLAlchemy |
| Database | PostgreSQL + PostGIS |
| ML | CatBoost, LightGBM, scikit-learn, NLTK |
| AI Copilot | Gemini API / OpenAI, LangChain, FAISS |
| Maps | MapLibre GL JS, Turf.js |
| Deployment | Docker, Vercel (frontend), Railway/Render (backend) |

## Why This Will Reach the Finale

1. **Real data, real product** — Not a toy dashboard; a system traffic police could actually use
2. **Prediction + Recommendation** — Goes beyond analysis to actionable intelligence
3. **AI Copilot** — Unique differentiator that no parking or CV solution can match
4. **Bengaluru-specific** — Uses actual Bengaluru corridors, zones, junctions, police stations
5. **Complete lifecycle** — From incident detection to post-event learning
6. **5-minute demo impact** — Live map, predictions, AI conversation, resource dispatch
