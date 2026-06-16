# 24-Hour Sprint Plan

## Hour 0–2: Foundation (2h)

- [ ] Set up monorepo: `frontend/` (Next.js) + `backend/` (FastAPI) + `ml/` (training)
- [ ] Initialize PostgreSQL + PostGIS on Supabase
- [ ] Run `schema.sql` — create incidents, predictions, resources tables
- [ ] Load Astram CSV into `incidents` table
- [ ] Verify: `SELECT count(*) FROM incidents;` → 8173

## Hour 2–6: ML Pipeline (4h)

- [ ] Feature engineering script: parse timestamps, extract hour/dow, encode categoricals
- [ ] Clean data: drop 100% null cols, handle anomalies (48 negative durations, 22 extreme outliers)
- [ ] Train Model 1: Priority Classifier (CatBoost, 5-fold CV)
- [ ] Train Model 2: Road Closure Predictor (LightGBM, handle imbalance)
- [ ] Train Model 3: Resolution Time Regressor (CatBoost, log-transform)
- [ ] Build Similar Incident search (TF-IDF + cosine similarity, pre-compute matrix)
- [ ] Serialize all models: `.cbm`, `.lgb`, `.pkl`
- [ ] Evaluate: print F1, AUC, MAE per model

## Hour 6–10: Backend API (4h)

- [ ] FastAPI skeleton: incidents CRUD, predictions endpoint, search endpoint
- [ ] Model loading at startup
- [ ] `/api/predict/enrich` — full prediction pipeline
- [ ] `/api/search/similar` — top-K similar incidents
- [ ] `/api/analytics/corridors` — corridor risk scores
- [ ] `/api/analytics/hotspots` — DBSCAN cluster centroids
- [ ] WebSocket for real-time incident feed
- [ ] CORS, error handling, logging

## Hour 10–16: Frontend — Map & Dashboard (6h)

- [ ] Next.js project with MapLibre GL JS
- [ ] Incident markers on map (color by priority)
- [ ] Heatmap toggle layer
- [ ] Incident detail panel (click marker → see predictions, similar incidents)
- [ ] New Incident form → POST to API → show enriched result
- [ ] Corridor risk sidebar
- [ ] Time slider for historical playback

## Hour 16–20: AI Copilot (4h)

- [ ] Chat UI component (bottom-right panel)
- [ ] Backend: `/api/copilot/chat` endpoint
- [ ] Intent classification (keyword-based)
- [ ] Context retrieval from DB + predictions API
- [ ] Gemini API integration for generation
- [ ] Response formatting with action buttons
- [ ] Test with 5 example queries

## Hour 20–24: Polish & Deploy (4h)

- [ ] Responsive layout fixes
- [ ] Loading states, error boundaries
- [ ] Deploy frontend → Vercel
- [ ] Deploy backend → Railway
- [ ] End-to-end smoke test
- [ ] Record 2-minute demo video as backup
- [ ] Prepare 5-minute live demo flow

---

## 24-Hour Deliverables

| Deliverable | Status |
|---|---|
| Working map with 8173 incidents | ⬜ |
| 3 ML models trained and serving | ⬜ |
| Prediction API (severity, closure, resolution time) | ⬜ |
| Similar incident search | ⬜ |
| AI Copilot with 5 working queries | ⬜ |
| Deployed to cloud (Vercel + Railway) | ⬜ |
| Live demo rehearsed | ⬜ |
