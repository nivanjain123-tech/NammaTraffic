# Final Submission Checklist

## Code & Repository
- [ ] GitHub repository created and public (or shared with judges)
- [ ] README.md with project overview, setup instructions, screenshots
- [ ] Clean folder structure: `frontend/`, `backend/`, `ml/`, `docs/`
- [ ] `.env.example` with all required environment variables listed
- [ ] `requirements.txt` / `package.json` with all dependencies
- [ ] `docker-compose.yml` for local setup
- [ ] All code linted and formatted

## ML Models
- [ ] 3+ trained models serialized (`.cbm`, `.lgb`, `.pkl`)
- [ ] Training script reproducible (`python train.py`)
- [ ] Evaluation metrics documented (F1, AUC, MAE, R²)
- [ ] Feature importance plots saved
- [ ] Cross-validation results logged

## Data
- [ ] Astram dataset loaded into PostgreSQL
- [ ] Data cleaning pipeline documented
- [ ] Feature engineering pipeline documented
- [ ] No PII in any exposed endpoint or screenshot

## Backend
- [ ] FastAPI server running and accessible
- [ ] All API endpoints working (test with curl/Postman)
- [ ] `/api/predict/enrich` returns predictions in <200ms
- [ ] `/api/search/similar` returns top-5 in <500ms
- [ ] `/api/copilot/chat` returns response in <5s
- [ ] Error handling and input validation
- [ ] CORS configured for frontend domain

## Frontend
- [ ] Next.js app deployed and accessible via URL
- [ ] Map rendering with all 8173 incidents
- [ ] Heatmap layer toggle working
- [ ] Incident detail panel shows predictions
- [ ] New incident form → enriched response
- [ ] AI Copilot chat interface functional
- [ ] Responsive on laptop screen (1366px+)
- [ ] No console errors in production

## Deployment
- [ ] Frontend deployed (Vercel / Netlify)
- [ ] Backend deployed (Railway / Render)
- [ ] Database provisioned (Supabase / Railway)
- [ ] All environment variables configured
- [ ] HTTPS working
- [ ] Smoke test: create incident → see predictions → ask copilot

## Demo Preparation
- [ ] 5-minute demo script finalized
- [ ] 3 scenarios pre-loaded and tested
- [ ] Backup: 2-minute demo video recorded
- [ ] Slides ready (if required): problem, solution, architecture, results, impact
- [ ] Browser bookmarks set for quick navigation
- [ ] Incognito window tested (no caching issues)
- [ ] Internet backup plan (mobile hotspot)

## Documentation
- [ ] Architecture overview diagram
- [ ] Product definition document
- [ ] ML model performance report
- [ ] Demo script
- [ ] API documentation
- [ ] Handover bundle complete

## Final Checks (1 hour before submission)
- [ ] All URLs accessible from a different device
- [ ] Database has data (not wiped by deployment)
- [ ] ML models loaded (check `/api/health`)
- [ ] Map tiles loading correctly
- [ ] Copilot responding to at least 5 test queries
- [ ] No placeholder text or "TODO" visible in UI
- [ ] Team member names and roles listed in README
- [ ] Submission form filled completely on HackerEarth
