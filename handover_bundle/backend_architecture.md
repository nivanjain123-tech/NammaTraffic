# ⚙️ Backend Architecture — NammaTraffic
## FastAPI Event-Driven Processing Engine

> **Framework:** FastAPI 0.111+ (Python 3.11+)
> **Server:** Uvicorn (ASGI)
> **ORM:** SQLAlchemy 2.0 + GeoAlchemy2
> **Task Queue:** Background Tasks (FastAPI) + APScheduler

---

## 1. Backend Philosophy

> *"The backend is an event processing pipeline with an API attached, not a CRUD server with some business logic."*

### Core Principles
1. **Event-First** — Every incident is an event flowing through a pipeline
2. **Async-Native** — All I/O operations are async (database, HTTP, WebSocket)
3. **Service Layer Pattern** — Controllers are thin; logic lives in services
4. **Fail-Safe ML** — ML predictions are non-blocking; system works without them
5. **Observable** — Structured logging, request tracing, health checks

---

## 2. Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI app factory
│   ├── config.py                   # Settings (Pydantic BaseSettings)
│   │
│   ├── api/                        # API Layer (Controllers)
│   │   ├── __init__.py
│   │   ├── deps.py                 # Dependency injection
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py           # Main v1 router
│   │   │   ├── incidents.py        # /incidents endpoints
│   │   │   ├── predictions.py      # /predictions endpoints
│   │   │   ├── analytics.py        # /analytics endpoints
│   │   │   ├── copilot.py          # /copilot endpoints
│   │   │   ├── resources.py        # /resources endpoints
│   │   │   ├── corridors.py        # /corridors endpoints
│   │   │   ├── health.py           # /health endpoints
│   │   │   └── websocket.py        # WebSocket handlers
│   │   └── schemas/                # Pydantic request/response models
│   │       ├── __init__.py
│   │       ├── incident.py
│   │       ├── prediction.py
│   │       ├── analytics.py
│   │       ├── copilot.py
│   │       └── common.py
│   │
│   ├── services/                   # Business Logic Layer
│   │   ├── __init__.py
│   │   ├── incident_service.py     # Incident CRUD + lifecycle
│   │   ├── prediction_service.py   # ML model orchestration
│   │   ├── geo_service.py          # Geospatial operations
│   │   ├── analytics_service.py    # Aggregations + stats
│   │   ├── copilot_service.py      # LLM + RAG orchestration
│   │   ├── resource_service.py     # Resource dispatch logic
│   │   └── notification_service.py # WebSocket broadcast
│   │
│   ├── ml/                         # ML Engine
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── severity_model.py
│   │   │   ├── resolution_model.py
│   │   │   ├── closure_model.py
│   │   │   └── resource_model.py
│   │   ├── features/
│   │   │   ├── feature_engineer.py
│   │   │   └── feature_store.py
│   │   ├── training/
│   │   │   └── train_pipeline.py
│   │   └── artifacts/              # Saved model files
│   │       ├── severity_model.joblib
│   │       ├── resolution_model.joblib
│   │       └── closure_model.joblib
│   │
│   ├── copilot/                    # AI Copilot Engine
│   │   ├── __init__.py
│   │   ├── llm_router.py           # LLM provider abstraction
│   │   ├── rag_engine.py           # ChromaDB RAG
│   │   ├── prompts/
│   │   │   ├── system_prompt.py
│   │   │   ├── incident_analysis.py
│   │   │   ├── corridor_query.py
│   │   │   └── resource_recommendation.py
│   │   └── tools/                  # Function calling tools for LLM
│   │       ├── query_incidents.py
│   │       ├── get_analytics.py
│   │       └── get_predictions.py
│   │
│   ├── db/                         # Data Access Layer
│   │   ├── __init__.py
│   │   ├── base.py                 # SQLAlchemy Base
│   │   ├── session.py              # Engine + SessionLocal
│   │   └── repositories/
│   │       ├── incident_repo.py
│   │       ├── prediction_repo.py
│   │       ├── analytics_repo.py
│   │       └── resource_repo.py
│   │
│   ├── models/                     # SQLAlchemy ORM Models
│   │   ├── __init__.py
│   │   ├── incident.py
│   │   ├── prediction.py
│   │   ├── corridor.py
│   │   ├── zone.py
│   │   ├── resource.py
│   │   └── copilot.py
│   │
│   ├── pipeline/                   # Event Processing Pipeline
│   │   ├── __init__.py
│   │   ├── ingestion.py            # Data ingestion handlers
│   │   ├── enrichment.py           # Geo + temporal enrichment
│   │   ├── scoring.py              # ML scoring pipeline
│   │   └── dispatcher.py           # Auto-dispatch logic
│   │
│   └── core/                       # Cross-cutting Concerns
│       ├── __init__.py
│       ├── security.py             # JWT auth, RBAC
│       ├── middleware.py           # CORS, logging, timing
│       ├── exceptions.py          # Custom exceptions
│       ├── logging.py             # Structured logging
│       └── cache.py               # Redis operations
│
├── scripts/
│   ├── load_dataset.py             # Load CSV into PostgreSQL
│   ├── seed_references.py          # Seed corridors, zones, junctions
│   ├── train_models.py             # Train ML models
│   ├── build_rag_index.py          # Build ChromaDB vector index
│   └── simulate_realtime.py        # Simulate real-time feed for demo
│
├── tests/
│   ├── conftest.py
│   ├── test_incidents.py
│   ├── test_predictions.py
│   └── test_copilot.py
│
├── alembic/                        # Database migrations
│   ├── alembic.ini
│   └── versions/
│
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## 3. Application Factory

```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.config import settings
from app.api.v1.router import api_router
from app.core.middleware import RequestTimingMiddleware, StructuredLoggingMiddleware
from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.ml.models.severity_model import SeverityModel
from app.ml.models.resolution_model import ResolutionModel
from app.ml.models.closure_model import ClosureModel
from app.copilot.rag_engine import RAGEngine
from app.core.cache import RedisCache
from app.services.notification_service import WebSocketManager

import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    logger.info("🚀 Starting NammaTraffic Backend...")
    
    # Initialize database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database initialized")
    
    # Load ML models
    app.state.severity_model = SeverityModel.load(settings.ML_ARTIFACTS_DIR / "severity_model.joblib")
    app.state.resolution_model = ResolutionModel.load(settings.ML_ARTIFACTS_DIR / "resolution_model.joblib")
    app.state.closure_model = ClosureModel.load(settings.ML_ARTIFACTS_DIR / "closure_model.joblib")
    logger.info("✅ ML models loaded")
    
    # Initialize RAG engine
    app.state.rag_engine = RAGEngine(
        collection_name="incidents",
        persist_directory=str(settings.CHROMA_DIR),
    )
    logger.info("✅ RAG engine initialized")
    
    # Initialize Redis cache
    app.state.cache = RedisCache(settings.REDIS_URL)
    logger.info("✅ Redis cache connected")
    
    # Initialize WebSocket manager
    app.state.ws_manager = WebSocketManager()
    
    yield
    
    # Cleanup
    await app.state.cache.close()
    logger.info("👋 NammaTraffic Backend shutdown complete")


def create_app() -> FastAPI:
    app = FastAPI(
        title="NammaTraffic API",
        description="Bengaluru Traffic Incident Intelligence & Command Platform",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Middleware (order matters — last added = first executed)
    app.add_middleware(GZipMiddleware, minimum_size=500)
    app.add_middleware(RequestTimingMiddleware)
    app.add_middleware(StructuredLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Routes
    app.include_router(api_router, prefix="/api/v1")
    
    return app


app = create_app()
```

---

## 4. Configuration

```python
# app/config.py
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import List


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "NammaTraffic"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://namma:traffic@localhost:5432/nammatraffic"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # ML
    ML_ARTIFACTS_DIR: Path = Path("app/ml/artifacts")
    
    # ChromaDB
    CHROMA_DIR: Path = Path("app/copilot/chroma_data")
    
    # LLM
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    
    # Embeddings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    class Config:
        env_file = ".env"


settings = Settings()
```

---

## 5. Event Processing Pipeline

### 5.1 Pipeline Architecture

```mermaid
graph LR
    subgraph "Ingestion"
        I1["API Endpoint<br/>POST /incidents"]
        I2["CSV Loader<br/>(Batch)"]
        I3["Webhook<br/>(External)"]
    end

    subgraph "Validation"
        V1["Pydantic<br/>Schema Validation"]
        V2["Deduplication<br/>Check"]
    end

    subgraph "Enrichment"
        E1["Geo-Enrichment<br/>zone, junction, corridor"]
        E2["Temporal Features<br/>hour, day, peak flag"]
        E3["Historical Context<br/>nearby incidents, corridor stats"]
    end

    subgraph "Scoring"
        S1["Severity Model"]
        S2["Resolution Model"]
        S3["Closure Model"]
        S4["Resource Model"]
    end

    subgraph "Output"
        O1["PostgreSQL<br/>(Persist)"]
        O2["WebSocket<br/>(Broadcast)"]
        O3["Redis<br/>(Cache Update)"]
    end

    I1 --> V1
    I2 --> V1
    I3 --> V1
    V1 --> V2
    V2 --> E1
    E1 --> E2
    E2 --> E3
    E3 --> S1
    S1 --> S2
    S2 --> S3
    S3 --> S4
    S4 --> O1
    S4 --> O2
    S4 --> O3
```

### 5.2 Pipeline Implementation

```python
# app/pipeline/ingestion.py
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from app.api.schemas.incident import IncidentCreate
from app.pipeline.enrichment import GeoEnricher, TemporalEnricher, HistoricalEnricher
from app.pipeline.scoring import MLScorer
from app.db.repositories.incident_repo import IncidentRepository
from app.services.notification_service import WebSocketManager
from app.core.cache import RedisCache

import logging

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    incident_id: str
    predictions: dict
    enrichments: dict
    processing_time_ms: float
    errors: list[str]


class IncidentPipeline:
    """
    Processes incoming incidents through validation → enrichment → scoring → persistence.
    Designed to be fault-tolerant: if ML scoring fails, the incident is still persisted.
    """

    def __init__(
        self,
        incident_repo: IncidentRepository,
        geo_enricher: GeoEnricher,
        temporal_enricher: TemporalEnricher,
        historical_enricher: HistoricalEnricher,
        ml_scorer: MLScorer,
        ws_manager: WebSocketManager,
        cache: RedisCache,
    ):
        self.incident_repo = incident_repo
        self.geo_enricher = geo_enricher
        self.temporal_enricher = temporal_enricher
        self.historical_enricher = historical_enricher
        self.ml_scorer = ml_scorer
        self.ws_manager = ws_manager
        self.cache = cache

    async def process(self, incident_data: IncidentCreate) -> PipelineResult:
        """Process a single incident through the full pipeline."""
        start_time = datetime.utcnow()
        errors = []

        # Step 1: Geo-Enrichment
        try:
            geo_context = await self.geo_enricher.enrich(
                lat=incident_data.latitude,
                lng=incident_data.longitude,
            )
            incident_data.zone_id = geo_context.zone_id
            incident_data.junction_id = geo_context.nearest_junction_id
            incident_data.corridor_id = geo_context.corridor_id
        except Exception as e:
            logger.warning(f"Geo-enrichment failed: {e}")
            errors.append(f"geo_enrichment: {str(e)}")
            geo_context = None

        # Step 2: Temporal Enrichment
        temporal_features = self.temporal_enricher.extract(incident_data.start_datetime)

        # Step 3: Historical Context
        try:
            historical_context = await self.historical_enricher.get_context(
                lat=incident_data.latitude,
                lng=incident_data.longitude,
                radius_m=500,
                event_cause=incident_data.event_cause,
            )
        except Exception as e:
            logger.warning(f"Historical enrichment failed: {e}")
            errors.append(f"historical_enrichment: {str(e)}")
            historical_context = None

        # Step 4: Persist Incident
        incident = await self.incident_repo.create(incident_data)

        # Step 5: ML Scoring (non-blocking)
        predictions = {}
        try:
            predictions = await self.ml_scorer.score(
                incident=incident,
                geo_context=geo_context,
                temporal_features=temporal_features,
                historical_context=historical_context,
            )
        except Exception as e:
            logger.error(f"ML scoring failed for {incident.id}: {e}")
            errors.append(f"ml_scoring: {str(e)}")

        # Step 6: Broadcast via WebSocket
        await self.ws_manager.broadcast({
            "type": "incident_new",
            "data": {
                "id": str(incident.id),
                "event_cause": incident.event_cause,
                "priority": incident.priority,
                "latitude": incident_data.latitude,
                "longitude": incident_data.longitude,
                "predictions": predictions,
            },
        })

        # Step 7: Update Redis cache
        await self.cache.invalidate("incidents:active:geojson")
        await self.cache.increment("dashboard:counters:total_active")

        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

        return PipelineResult(
            incident_id=str(incident.id),
            predictions=predictions,
            enrichments={
                "geo": geo_context.__dict__ if geo_context else None,
                "temporal": temporal_features,
                "historical": historical_context,
            },
            processing_time_ms=processing_time,
            errors=errors,
        )
```

### 5.3 Enrichment Services

```python
# app/pipeline/enrichment.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class GeoContext:
    zone_id: Optional[str]
    zone_name: Optional[str]
    nearest_junction_id: Optional[str]
    nearest_junction_name: Optional[str]
    junction_distance_m: Optional[float]
    corridor_id: Optional[str]
    corridor_name: Optional[str]
    police_station_id: Optional[str]
    road_type: Optional[str]


class GeoEnricher:
    """Enriches incidents with spatial context using PostGIS queries."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def enrich(self, lat: float, lng: float) -> GeoContext:
        """Find zone, nearest junction, corridor for a point."""
        
        # Find containing zone
        zone_result = await self.db.execute(text("""
            SELECT id, name FROM zones
            WHERE ST_Contains(boundary, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326))
            LIMIT 1
        """), {"lat": lat, "lng": lng})
        zone = zone_result.first()

        # Find nearest junction (within 2km)
        junction_result = await self.db.execute(text("""
            SELECT id, name,
                   ST_Distance(location::geography, 
                               ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography) as distance_m
            FROM junctions
            WHERE ST_DWithin(location::geography, 
                             ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography, 2000)
            ORDER BY distance_m
            LIMIT 1
        """), {"lat": lat, "lng": lng})
        junction = junction_result.first()

        # Find nearest corridor (within 500m of the corridor line)
        corridor_result = await self.db.execute(text("""
            SELECT id, name FROM corridors
            WHERE ST_DWithin(route_line::geography,
                             ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography, 500)
            ORDER BY ST_Distance(route_line::geography,
                                 ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography)
            LIMIT 1
        """), {"lat": lat, "lng": lng})
        corridor = corridor_result.first()

        # Find nearest police station
        ps_result = await self.db.execute(text("""
            SELECT id, name FROM police_stations
            ORDER BY location <-> ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)
            LIMIT 1
        """), {"lat": lat, "lng": lng})
        police_station = ps_result.first()

        return GeoContext(
            zone_id=zone.id if zone else None,
            zone_name=zone.name if zone else None,
            nearest_junction_id=junction.id if junction else None,
            nearest_junction_name=junction.name if junction else None,
            junction_distance_m=junction.distance_m if junction else None,
            corridor_id=corridor.id if corridor else None,
            corridor_name=corridor.name if corridor else None,
            police_station_id=police_station.id if police_station else None,
            road_type=None,  # Would need road network data
        )


class TemporalEnricher:
    """Extracts temporal features from timestamps."""

    @staticmethod
    def extract(dt: datetime) -> dict:
        ist_hour = (dt.hour + 5) % 24 + (30 // 60)  # UTC to IST
        
        return {
            "hour": ist_hour,
            "day_of_week": dt.weekday(),
            "day_name": dt.strftime("%A"),
            "month": dt.month,
            "is_weekend": dt.weekday() >= 5,
            "is_peak_morning": 8 <= ist_hour <= 10,
            "is_peak_evening": 17 <= ist_hour <= 20,
            "is_peak": (8 <= ist_hour <= 10) or (17 <= ist_hour <= 20),
            "is_night": ist_hour >= 22 or ist_hour <= 5,
            "time_slot": categorize_time_slot(ist_hour),
        }


def categorize_time_slot(hour: int) -> str:
    if 5 <= hour < 8: return "early_morning"
    if 8 <= hour < 11: return "morning_peak"
    if 11 <= hour < 14: return "midday"
    if 14 <= hour < 17: return "afternoon"
    if 17 <= hour < 21: return "evening_peak"
    if 21 <= hour < 24: return "late_evening"
    return "night"


class HistoricalEnricher:
    """Provides historical context for an incident location."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_context(
        self, lat: float, lng: float, radius_m: int, event_cause: str
    ) -> dict:
        """Get historical incident patterns near this location."""
        
        result = await self.db.execute(text("""
            SELECT 
                COUNT(*) as total_nearby,
                COUNT(*) FILTER (WHERE event_cause = :cause) as same_cause_count,
                AVG(duration_minutes) as avg_resolution_min,
                COUNT(*) FILTER (WHERE requires_road_closure) as closure_count,
                COUNT(*) FILTER (WHERE priority = 'High') as high_priority_count,
                MAX(start_datetime) as last_incident_at
            FROM incidents
            WHERE ST_DWithin(
                location::geography,
                ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography,
                :radius
            )
            AND start_datetime >= NOW() - INTERVAL '90 days'
        """), {"lat": lat, "lng": lng, "radius": radius_m, "cause": event_cause})
        
        row = result.first()
        
        return {
            "nearby_incident_count_90d": row.total_nearby if row else 0,
            "same_cause_count_90d": row.same_cause_count if row else 0,
            "avg_resolution_minutes": float(row.avg_resolution_min) if row and row.avg_resolution_min else None,
            "historical_closure_rate": (
                row.closure_count / row.total_nearby if row and row.total_nearby > 0 else 0
            ),
            "is_repeat_location": (row.total_nearby > 5) if row else False,
            "last_incident_days_ago": (
                (datetime.utcnow() - row.last_incident_at).days if row and row.last_incident_at else None
            ),
        }
```

---

## 6. Service Layer

### 6.1 Incident Service

```python
# app/services/incident_service.py
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from geoalchemy2.functions import ST_DWithin, ST_MakePoint, ST_SetSRID

from app.models.incident import Incident
from app.api.schemas.incident import IncidentCreate, IncidentUpdate, IncidentFilters
from app.db.repositories.incident_repo import IncidentRepository


class IncidentService:
    def __init__(self, db: AsyncSession):
        self.repo = IncidentRepository(db)
        self.db = db

    async def get_active_incidents(self) -> List[Incident]:
        """Get all non-closed incidents for map display."""
        return await self.repo.find_by_status(["open", "active", "dispatched"])

    async def get_incidents_filtered(self, filters: IncidentFilters) -> dict:
        """Get paginated, filtered incidents."""
        query = select(Incident)

        if filters.event_causes:
            query = query.where(Incident.event_cause.in_(filters.event_causes))
        if filters.priorities:
            query = query.where(Incident.priority.in_(filters.priorities))
        if filters.statuses:
            query = query.where(Incident.status.in_(filters.statuses))
        if filters.corridor_id:
            query = query.where(Incident.corridor_id == filters.corridor_id)
        if filters.zone_id:
            query = query.where(Incident.zone_id == filters.zone_id)
        if filters.start_date:
            query = query.where(Incident.start_datetime >= filters.start_date)
        if filters.end_date:
            query = query.where(Incident.start_datetime <= filters.end_date)
        if filters.requires_road_closure is not None:
            query = query.where(Incident.requires_road_closure == filters.requires_road_closure)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar()

        # Paginate
        query = query.order_by(Incident.start_datetime.desc())
        query = query.offset(filters.offset).limit(filters.limit)

        result = await self.db.execute(query)
        incidents = result.scalars().all()

        return {
            "total": total,
            "page": filters.page,
            "per_page": filters.limit,
            "items": incidents,
        }

    async def get_incidents_geojson(self, filters: Optional[IncidentFilters] = None) -> dict:
        """Get incidents as GeoJSON FeatureCollection for map rendering."""
        incidents = await self.get_active_incidents()
        
        return {
            "type": "FeatureCollection",
            "features": [inc.to_geojson() for inc in incidents],
            "metadata": {
                "total": len(incidents),
                "generated_at": datetime.utcnow().isoformat(),
            },
        }

    async def get_nearby_incidents(
        self, lat: float, lng: float, radius_m: int = 1000
    ) -> List[Incident]:
        """Find incidents near a point using PostGIS."""
        query = select(Incident).where(
            and_(
                Incident.status.in_(["open", "active", "dispatched"]),
                ST_DWithin(
                    Incident.location,
                    ST_SetSRID(ST_MakePoint(lng, lat), 4326),
                    radius_m / 111320,  # Approximate degrees
                ),
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_status(
        self, incident_id: UUID, new_status: str, changed_by: Optional[UUID] = None
    ) -> Incident:
        """Update incident status with audit trail."""
        incident = await self.repo.get(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        old_status = incident.status
        incident.status = new_status
        incident.updated_at = datetime.utcnow()

        if new_status == "resolved":
            incident.resolved_at = datetime.utcnow()
        elif new_status == "closed":
            incident.closed_at = datetime.utcnow()

        # Create timeline entry
        await self.repo.add_timeline_entry(
            incident_id=incident_id,
            previous_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
        )

        await self.db.commit()
        return incident
```

---

## 7. WebSocket Real-Time Manager

```python
# app/services/notification_service.py
from typing import Dict, Set
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections for real-time incident updates."""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, Set[str]] = {
            "incidents": set(),
            "predictions": set(),
            "analytics": set(),
        }

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.subscriptions["incidents"].add(client_id)
        logger.info(f"WebSocket connected: {client_id} (total: {len(self.active_connections)})")

    def disconnect(self, client_id: str):
        self.active_connections.pop(client_id, None)
        for channel in self.subscriptions.values():
            channel.discard(client_id)
        logger.info(f"WebSocket disconnected: {client_id}")

    async def broadcast(self, message: dict, channel: str = "incidents"):
        """Broadcast message to all subscribed clients."""
        payload = json.dumps(message)
        disconnected = []

        for client_id in self.subscriptions.get(channel, set()):
            ws = self.active_connections.get(client_id)
            if ws:
                try:
                    await ws.send_text(payload)
                except Exception:
                    disconnected.append(client_id)

        for client_id in disconnected:
            self.disconnect(client_id)

    async def send_to_client(self, client_id: str, message: dict):
        """Send message to a specific client."""
        ws = self.active_connections.get(client_id)
        if ws:
            await ws.send_text(json.dumps(message))


# WebSocket endpoint
# app/api/v1/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import uuid

router = APIRouter()


@router.websocket("/ws/incidents")
async def incident_feed(websocket: WebSocket):
    """Real-time incident feed via WebSocket."""
    from app.main import app
    
    client_id = str(uuid.uuid4())
    ws_manager = app.state.ws_manager

    await ws_manager.connect(websocket, client_id)

    try:
        # Send initial sync
        from app.services.incident_service import IncidentService
        incidents = await IncidentService(get_db()).get_active_incidents()
        await ws_manager.send_to_client(client_id, {
            "type": "bulk_sync",
            "data": [inc.to_dict() for inc in incidents],
        })

        # Keep connection alive, handle incoming messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "subscribe":
                channel = message.get("channel", "incidents")
                ws_manager.subscriptions.setdefault(channel, set()).add(client_id)
            elif message.get("type") == "ping":
                await ws_manager.send_to_client(client_id, {"type": "pong"})

    except WebSocketDisconnect:
        ws_manager.disconnect(client_id)
```

---

## 8. Background Tasks & Scheduling

```python
# app/core/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

import logging

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def refresh_dashboard_cache():
    """Refresh Redis dashboard counters every 30 seconds."""
    from app.services.analytics_service import AnalyticsService
    service = AnalyticsService(get_db())
    counters = await service.compute_dashboard_counters()
    await cache.set("dashboard:counters", counters, ttl=60)
    logger.debug("Dashboard cache refreshed")


async def refresh_geojson_cache():
    """Refresh active incidents GeoJSON every 30 seconds."""
    from app.services.incident_service import IncidentService
    service = IncidentService(get_db())
    geojson = await service.get_incidents_geojson()
    await cache.set("incidents:active:geojson", geojson, ttl=60)


async def detect_hotspots():
    """Run hotspot detection every 15 minutes."""
    from app.services.geo_service import GeoService
    service = GeoService(get_db())
    hotspots = await service.detect_hotspots(time_window="hourly")
    logger.info(f"Detected {len(hotspots)} hotspots")


async def refresh_materialized_views():
    """Refresh materialized views every hour."""
    from app.db.session import engine
    async with engine.begin() as conn:
        await conn.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_stats"))
    logger.info("Materialized views refreshed")


def setup_scheduler():
    scheduler.add_job(refresh_dashboard_cache, IntervalTrigger(seconds=30))
    scheduler.add_job(refresh_geojson_cache, IntervalTrigger(seconds=30))
    scheduler.add_job(detect_hotspots, IntervalTrigger(minutes=15))
    scheduler.add_job(refresh_materialized_views, CronTrigger(minute=0))
    scheduler.start()
    logger.info("⏰ Scheduler started")
```

---

## 9. Real-Time Demo Simulator

```python
# scripts/simulate_realtime.py
"""
Simulates real-time incident feed by replaying historical data.
Used during demo to show the platform's real-time capabilities.
"""
import asyncio
import random
import httpx
from datetime import datetime

# Sample incidents for simulation
DEMO_INCIDENTS = [
    {
        "event_type": "unplanned",
        "event_cause": "accident",
        "latitude": 12.9352,
        "longitude": 77.6245,
        "address": "Silk Board Junction, BTM Layout",
        "priority": "High",
        "requires_road_closure": True,
        "description": "Multi-vehicle collision at Silk Board. 3 vehicles involved. Traffic backed up 2km.",
        "vehicle_type": "car",
        "corridor_id": "hosur_road",
    },
    {
        "event_type": "unplanned",
        "event_cause": "vehicle_breakdown",
        "latitude": 13.0358,
        "longitude": 77.5970,
        "address": "Hebbal Flyover, near Esteem Mall",
        "priority": "Medium",
        "requires_road_closure": False,
        "description": "Heavy truck breakdown on Hebbal flyover. Right lane blocked.",
        "vehicle_type": "heavy_vehicle",
        "corridor_id": "bellary_road",
    },
    {
        "event_type": "unplanned",
        "event_cause": "tree_fall",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "address": "MG Road, near Trinity Circle",
        "priority": "High",
        "requires_road_closure": True,
        "description": "Large tree fallen across MG Road. Both lanes blocked. BBMP notified.",
        "corridor_id": "non_corridor",
    },
]


async def simulate():
    """Replay incidents every 15-30 seconds during demo."""
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        while True:
            incident = random.choice(DEMO_INCIDENTS)
            incident["start_datetime"] = datetime.utcnow().isoformat()
            
            response = await client.post("/api/v1/incidents", json=incident)
            print(f"📡 Sent: {incident['event_cause']} at {incident['address'][:30]}... "
                  f"Status: {response.status_code}")
            
            await asyncio.sleep(random.uniform(15, 30))


if __name__ == "__main__":
    asyncio.run(simulate())
```

---

## 10. Error Handling & Middleware

```python
# app/core/middleware.py
import time
import logging
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        
        start = time.perf_counter()
        response: Response = await call_next(request)
        duration = (time.perf_counter() - start) * 1000
        
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = f"{duration:.1f}"
        
        # Log slow requests
        if duration > 500:
            logger.warning(
                f"SLOW REQUEST [{request_id}] {request.method} {request.url.path} "
                f"took {duration:.1f}ms"
            )
        
        return response


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(
            f"→ {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown",
            },
        )
        response = await call_next(request)
        logger.info(
            f"← {response.status_code} {request.url.path}",
            extra={"status_code": response.status_code},
        )
        return response


# app/core/exceptions.py
from fastapi import HTTPException


class IncidentNotFound(HTTPException):
    def __init__(self, incident_id: str):
        super().__init__(status_code=404, detail=f"Incident {incident_id} not found")


class PredictionFailed(HTTPException):
    def __init__(self, incident_id: str, reason: str):
        super().__init__(
            status_code=503,
            detail=f"ML prediction failed for {incident_id}: {reason}",
        )


class RateLimitExceeded(HTTPException):
    def __init__(self):
        super().__init__(status_code=429, detail="Rate limit exceeded. Try again later.")
```

---

## 11. Dependency Injection

```python
# app/api/deps.py
from typing import AsyncGenerator
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import SessionLocal
from app.services.incident_service import IncidentService
from app.services.prediction_service import PredictionService
from app.services.copilot_service import CopilotService
from app.services.analytics_service import AnalyticsService
from app.services.geo_service import GeoService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_incident_service(db: AsyncSession = Depends(get_db)) -> IncidentService:
    return IncidentService(db)


def get_prediction_service(
    db: AsyncSession = Depends(get_db),
    request: Request = None,
) -> PredictionService:
    return PredictionService(
        db=db,
        severity_model=request.app.state.severity_model,
        resolution_model=request.app.state.resolution_model,
        closure_model=request.app.state.closure_model,
    )


def get_copilot_service(
    db: AsyncSession = Depends(get_db),
    request: Request = None,
) -> CopilotService:
    return CopilotService(
        db=db,
        rag_engine=request.app.state.rag_engine,
    )


def get_analytics_service(db: AsyncSession = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db)


def get_geo_service(db: AsyncSession = Depends(get_db)) -> GeoService:
    return GeoService(db)
```

---

*The backend is designed as a pipeline processor, not a CRUD server. Every incident flows through validation → enrichment → scoring → persistence → notification. ML scoring is non-blocking and fault-tolerant — the system always persists the incident even if predictions fail.*
