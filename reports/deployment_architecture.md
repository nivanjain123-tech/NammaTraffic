# Deployment Architecture

## Overview

Optimized for hackathon speed: deploy in under 30 minutes with zero cloud configuration complexity.

```
┌──────────────────────────────────────────────────┐
│                  DEPLOYMENT                       │
│                                                   │
│  ┌─────────┐    ┌──────────┐    ┌─────────────┐  │
│  │ Vercel  │    │ Railway  │    │ Supabase    │  │
│  │ Frontend│◄──►│ Backend  │◄──►│ PostgreSQL  │  │
│  │ Next.js │    │ FastAPI  │    │ + PostGIS   │  │
│  └─────────┘    └──────────┘    └─────────────┘  │
│                      ↑                            │
│               ┌──────┴──────┐                     │
│               │ ML Models   │                     │
│               │ (in-process)│                     │
│               └─────────────┘                     │
└──────────────────────────────────────────────────┘
```

---

## Option A: Hackathon Fast Deploy (Recommended)

| Component | Platform | Why |
|---|---|---|
| Frontend | **Vercel** | Zero-config Next.js deployment, free tier, instant CDN |
| Backend + ML | **Railway** | One-click Python deploy, supports Docker, free $5 credit |
| Database | **Supabase** | Free PostgreSQL with PostGIS, instant setup |
| AI Copilot | **Gemini API** | Free tier for hackathon, or OpenAI with $5 credit |

### Deploy Steps
```bash
# 1. Frontend (Vercel)
cd frontend && vercel --prod

# 2. Backend (Railway)
cd backend && railway up

# 3. Database (Supabase)
# Create project at supabase.com, enable PostGIS, run schema.sql
```

---

## Option B: Docker Compose (Local Demo)

```yaml
# docker-compose.yml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    
  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql://postgres:password@db:5432/gridlock
      GEMINI_API_KEY: ${GEMINI_API_KEY}
    depends_on: [db]
    volumes:
      - ./models:/app/models
  
  db:
    image: postgis/postgis:15-3.3
    environment:
      POSTGRES_DB: gridlock
      POSTGRES_PASSWORD: password
    ports: ["5432:5432"]
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./schema.sql:/docker-entrypoint-initdb.d/01-schema.sql

volumes:
  pgdata:
```

### Backend Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## CI/CD Pipeline

```
GitHub Push → GitHub Actions
    ├── Lint (ruff, eslint)
    ├── Test (pytest, jest)
    ├── Build Frontend → Deploy to Vercel
    └── Build Backend → Deploy to Railway
```

---

## Environment Variables

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `GEMINI_API_KEY` | AI copilot LLM access |
| `CORS_ORIGINS` | Frontend URL for CORS |
| `MODEL_PATH` | Path to serialized ML models |
| `JWT_SECRET` | Authentication token signing |

---

## Performance Targets

| Metric | Target |
|---|---|
| API response (prediction) | <200ms |
| Map tile load | <1s |
| WebSocket latency | <100ms |
| Copilot response | <3s |
| Cold start | <10s |
