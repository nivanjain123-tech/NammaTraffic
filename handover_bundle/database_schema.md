# 🗄️ Database Schema — NammaTraffic
## PostgreSQL + PostGIS Schema Design

> **Database:** PostgreSQL 16 + PostGIS 3.4
> **ORM:** SQLAlchemy 2.0 + GeoAlchemy2
> **Migrations:** Alembic

---

## 1. Entity-Relationship Diagram

```mermaid
erDiagram
    INCIDENTS ||--o{ PREDICTIONS : has
    INCIDENTS ||--o{ INCIDENT_TIMELINE : has
    INCIDENTS ||--o{ RESOURCE_ASSIGNMENTS : has
    INCIDENTS }o--|| CORRIDORS : belongs_to
    INCIDENTS }o--|| ZONES : belongs_to
    INCIDENTS }o--|| JUNCTIONS : near
    INCIDENTS }o--|| POLICE_STATIONS : assigned_to

    RESOURCES ||--o{ RESOURCE_ASSIGNMENTS : assigned_in
    RESOURCES }o--|| POLICE_STATIONS : based_at

    CORRIDORS ||--o{ CORRIDOR_SEGMENTS : contains
    ZONES ||--o{ POLICE_STATIONS : contains

    HOTSPOTS ||--o{ HOTSPOT_INCIDENTS : contains
    INCIDENTS ||--o{ HOTSPOT_INCIDENTS : part_of

    COPILOT_SESSIONS ||--o{ COPILOT_MESSAGES : contains
    WEATHER_SNAPSHOTS }o--|| ZONES : covers

    INCIDENTS {
        uuid id PK
        varchar event_type
        geometry location
        geometry end_location
        text address
        text end_address
        varchar event_cause
        boolean requires_road_closure
        timestamptz start_datetime
        timestamptz end_datetime
        varchar status
        varchar priority
        text description
        varchar vehicle_type
        varchar vehicle_number
        varchar corridor_id FK
        varchar zone_id FK
        varchar junction_id FK
        varchar police_station_id FK
        jsonb metadata
        timestamptz created_at
        timestamptz updated_at
    }

    PREDICTIONS {
        uuid id PK
        uuid incident_id FK
        float severity_score
        varchar severity_label
        float resolution_time_minutes
        float road_closure_probability
        jsonb recommended_resources
        float confidence
        varchar model_version
        timestamptz predicted_at
    }

    CORRIDORS {
        varchar id PK
        varchar name
        geometry route_line
        float length_km
        varchar category
    }

    ZONES {
        varchar id PK
        varchar name
        geometry boundary
    }

    JUNCTIONS {
        varchar id PK
        varchar name
        geometry location
        varchar zone_id FK
    }

    POLICE_STATIONS {
        varchar id PK
        varchar name
        geometry location
        varchar zone_id FK
    }

    RESOURCES {
        uuid id PK
        varchar type
        varchar unit_name
        geometry current_location
        varchar status
        varchar police_station_id FK
    }

    HOTSPOTS {
        uuid id PK
        geometry centroid
        geometry boundary
        float radius_m
        int incident_count
        varchar dominant_cause
        varchar time_window
        timestamptz detected_at
    }
```

---

## 2. Core Tables

### 2.1 `incidents` — Primary Incident Table

```sql
-- Enable PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- For text search
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE incidents (
    -- Identity
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id     VARCHAR(20) UNIQUE,  -- FKID000000 format from source
    
    -- Classification
    event_type      VARCHAR(20) NOT NULL CHECK (event_type IN ('planned', 'unplanned')),
    event_cause     VARCHAR(50) NOT NULL,
    priority        VARCHAR(10) NOT NULL DEFAULT 'Medium' 
                    CHECK (priority IN ('High', 'Medium', 'Low')),
    status          VARCHAR(20) NOT NULL DEFAULT 'open'
                    CHECK (status IN ('open', 'active', 'dispatched', 'resolved', 'closed')),
    
    -- Geospatial (PostGIS)
    location        GEOMETRY(Point, 4326) NOT NULL,  -- SRID 4326 = WGS84
    end_location    GEOMETRY(Point, 4326),
    address         TEXT,
    end_address     TEXT,
    
    -- Road Impact
    requires_road_closure BOOLEAN DEFAULT FALSE,
    affected_lanes  INTEGER DEFAULT 0,
    
    -- Temporal
    start_datetime  TIMESTAMPTZ NOT NULL,
    end_datetime    TIMESTAMPTZ,
    resolved_at     TIMESTAMPTZ,
    closed_at       TIMESTAMPTZ,
    
    -- Vehicle Info (for vehicle_breakdown, accident)
    vehicle_type    VARCHAR(30),
    vehicle_number  VARCHAR(20),
    cargo_material  VARCHAR(100),
    
    -- Description
    description     TEXT,
    
    -- Relationships
    corridor_id     VARCHAR(50) REFERENCES corridors(id),
    zone_id         VARCHAR(50) REFERENCES zones(id),
    junction_id     VARCHAR(50) REFERENCES junctions(id),
    police_station_id VARCHAR(50) REFERENCES police_stations(id),
    
    -- Computed Fields
    duration_minutes FLOAT GENERATED ALWAYS AS (
        EXTRACT(EPOCH FROM (COALESCE(end_datetime, NOW()) - start_datetime)) / 60
    ) STORED,
    
    -- Metadata
    authenticated   BOOLEAN DEFAULT FALSE,
    metadata        JSONB DEFAULT '{}',
    
    -- Audit
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    created_by      UUID,
    last_modified_by UUID
);

-- ============================================================
-- INDEXES — Optimized for the queries we actually run
-- ============================================================

-- Spatial index (R-tree) — THE most important index
CREATE INDEX idx_incidents_location ON incidents USING GIST (location);
CREATE INDEX idx_incidents_end_location ON incidents USING GIST (end_location);

-- Temporal indexes
CREATE INDEX idx_incidents_start_datetime ON incidents (start_datetime DESC);
CREATE INDEX idx_incidents_status ON incidents (status);
CREATE INDEX idx_incidents_status_start ON incidents (status, start_datetime DESC);

-- Composite filters (the actual query patterns)
CREATE INDEX idx_incidents_cause_status ON incidents (event_cause, status);
CREATE INDEX idx_incidents_priority_status ON incidents (priority, status);
CREATE INDEX idx_incidents_corridor ON incidents (corridor_id, start_datetime DESC);
CREATE INDEX idx_incidents_zone ON incidents (zone_id, start_datetime DESC);
CREATE INDEX idx_incidents_police_station ON incidents (police_station_id);

-- Text search on descriptions
CREATE INDEX idx_incidents_description_trgm ON incidents 
    USING GIN (description gin_trgm_ops);

-- JSONB metadata
CREATE INDEX idx_incidents_metadata ON incidents USING GIN (metadata);
```

### 2.2 `predictions` — ML Model Outputs

```sql
CREATE TABLE predictions (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id             UUID NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    
    -- Severity Prediction
    severity_score          FLOAT CHECK (severity_score BETWEEN 0 AND 1),
    severity_label          VARCHAR(20) CHECK (severity_label IN ('critical', 'high', 'medium', 'low')),
    
    -- Resolution Time Prediction  
    resolution_time_minutes FLOAT CHECK (resolution_time_minutes >= 0),
    resolution_time_lower   FLOAT,  -- 95% CI lower bound
    resolution_time_upper   FLOAT,  -- 95% CI upper bound
    
    -- Road Closure Prediction
    road_closure_probability FLOAT CHECK (road_closure_probability BETWEEN 0 AND 1),
    
    -- Resource Recommendation
    recommended_resources   JSONB DEFAULT '[]',
    /*
    Example:
    [
        {"type": "tow_truck", "count": 1, "priority": "immediate"},
        {"type": "traffic_police", "count": 2, "priority": "immediate"},
        {"type": "ambulance", "count": 1, "priority": "if_injury"}
    ]
    */
    
    -- Congestion Impact
    congestion_radius_m     FLOAT,
    estimated_delay_minutes FLOAT,
    affected_corridors      VARCHAR[] DEFAULT '{}',
    
    -- Model Metadata
    model_version           VARCHAR(20) NOT NULL,
    confidence              FLOAT CHECK (confidence BETWEEN 0 AND 1),
    feature_importance      JSONB DEFAULT '{}',
    
    -- Timing
    predicted_at            TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(incident_id, model_version)
);

CREATE INDEX idx_predictions_incident ON predictions (incident_id);
CREATE INDEX idx_predictions_severity ON predictions (severity_score DESC);
```

### 2.3 `incident_timeline` — Status Audit Trail

```sql
CREATE TABLE incident_timeline (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id     UUID NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    
    previous_status VARCHAR(20),
    new_status      VARCHAR(20) NOT NULL,
    
    changed_by      UUID,
    change_reason   TEXT,
    metadata        JSONB DEFAULT '{}',
    
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_timeline_incident ON incident_timeline (incident_id, created_at);
```

---

## 3. Reference Tables

### 3.1 `corridors` — Traffic Corridors

```sql
CREATE TABLE corridors (
    id          VARCHAR(50) PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    route_line  GEOMETRY(LineString, 4326),
    length_km   FLOAT,
    category    VARCHAR(20) DEFAULT 'arterial'
                CHECK (category IN ('arterial', 'sub-arterial', 'collector', 'local')),
    speed_limit_kmph INTEGER DEFAULT 40,
    
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_corridors_route ON corridors USING GIST (route_line);

-- Seed from dataset
INSERT INTO corridors (id, name, category) VALUES
    ('tumkur_road', 'Tumkur Road', 'arterial'),
    ('orr_east_1', 'ORR East 1', 'arterial'),
    ('orr_east_2', 'ORR East 2', 'arterial'),
    ('orr_west_1', 'ORR West 1', 'arterial'),
    ('orr_west_2', 'ORR West 2', 'arterial'),
    ('hosur_road', 'Hosur Road', 'arterial'),
    ('bellary_road', 'Bellary Road', 'arterial'),
    ('mysore_road', 'Mysore Road', 'arterial'),
    ('old_madras_road', 'Old Madras Road', 'arterial'),
    ('kanakapura_road', 'Kanakapura Road', 'sub-arterial'),
    ('sarjapur_road', 'Sarjapur Road', 'sub-arterial'),
    ('non_corridor', 'Non-corridor', 'local');
```

### 3.2 `zones` — BTP Zones

```sql
CREATE TABLE zones (
    id          VARCHAR(50) PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    boundary    GEOMETRY(Polygon, 4326),
    area_sq_km  FLOAT,
    
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_zones_boundary ON zones USING GIST (boundary);
```

### 3.3 `junctions` — Key Junctions

```sql
CREATE TABLE junctions (
    id          VARCHAR(50) PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    location    GEOMETRY(Point, 4326),
    zone_id     VARCHAR(50) REFERENCES zones(id),
    signal_type VARCHAR(30) DEFAULT 'signal'
                CHECK (signal_type IN ('signal', 'roundabout', 'uncontrolled', 'flyover')),
    
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_junctions_location ON junctions USING GIST (location);
```

### 3.4 `police_stations` — BTP Stations

```sql
CREATE TABLE police_stations (
    id              VARCHAR(50) PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    location        GEOMETRY(Point, 4326),
    zone_id         VARCHAR(50) REFERENCES zones(id),
    jurisdiction    GEOMETRY(Polygon, 4326),
    contact_number  VARCHAR(20),
    
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_police_stations_location ON police_stations USING GIST (location);
CREATE INDEX idx_police_stations_jurisdiction ON police_stations USING GIST (jurisdiction);
```

---

## 4. Resource Management Tables

### 4.1 `resources` — Dispatch Units

```sql
CREATE TABLE resources (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type                VARCHAR(30) NOT NULL
                        CHECK (type IN (
                            'tow_truck', 'traffic_police', 'ambulance',
                            'fire_engine', 'tree_cutter', 'road_crew',
                            'barricade_unit', 'signal_tech'
                        )),
    unit_name           VARCHAR(50) NOT NULL,
    current_location    GEOMETRY(Point, 4326),
    status              VARCHAR(20) DEFAULT 'available'
                        CHECK (status IN ('available', 'dispatched', 'en_route', 'on_scene', 'returning')),
    police_station_id   VARCHAR(50) REFERENCES police_stations(id),
    
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_resources_location ON resources USING GIST (current_location);
CREATE INDEX idx_resources_status_type ON resources (status, type);
```

### 4.2 `resource_assignments` — Dispatch Records

```sql
CREATE TABLE resource_assignments (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id     UUID NOT NULL REFERENCES incidents(id),
    resource_id     UUID NOT NULL REFERENCES resources(id),
    
    assigned_at     TIMESTAMPTZ DEFAULT NOW(),
    dispatched_at   TIMESTAMPTZ,
    arrived_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    
    eta_minutes     FLOAT,
    distance_km     FLOAT,
    
    status          VARCHAR(20) DEFAULT 'assigned'
                    CHECK (status IN ('assigned', 'dispatched', 'en_route', 'on_scene', 'completed', 'cancelled')),
    
    notes           TEXT
);

CREATE INDEX idx_assignments_incident ON resource_assignments (incident_id);
CREATE INDEX idx_assignments_resource ON resource_assignments (resource_id, status);
```

---

## 5. Analytics & Hotspot Tables

### 5.1 `hotspots` — Detected Incident Clusters

```sql
CREATE TABLE hotspots (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    centroid        GEOMETRY(Point, 4326) NOT NULL,
    boundary        GEOMETRY(Polygon, 4326),
    radius_m        FLOAT NOT NULL,
    
    incident_count  INTEGER NOT NULL,
    dominant_cause  VARCHAR(50),
    avg_severity    FLOAT,
    
    time_window     VARCHAR(20) NOT NULL
                    CHECK (time_window IN ('hourly', 'daily', 'weekly', 'monthly', 'all_time')),
    window_start    TIMESTAMPTZ,
    window_end      TIMESTAMPTZ,
    
    cluster_id      INTEGER,  -- From DBSCAN
    
    detected_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_hotspots_centroid ON hotspots USING GIST (centroid);
CREATE INDEX idx_hotspots_boundary ON hotspots USING GIST (boundary);
CREATE INDEX idx_hotspots_window ON hotspots (time_window, detected_at DESC);
```

### 5.2 `corridor_analytics` — Pre-computed Corridor Stats

```sql
CREATE TABLE corridor_analytics (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    corridor_id     VARCHAR(50) NOT NULL REFERENCES corridors(id),
    
    date            DATE NOT NULL,
    hour            INTEGER CHECK (hour BETWEEN 0 AND 23),
    
    incident_count  INTEGER DEFAULT 0,
    avg_resolution_min FLOAT,
    closure_count   INTEGER DEFAULT 0,
    
    breakdown_count INTEGER DEFAULT 0,
    accident_count  INTEGER DEFAULT 0,
    tree_fall_count INTEGER DEFAULT 0,
    
    severity_avg    FLOAT,
    
    UNIQUE(corridor_id, date, hour)
);

CREATE INDEX idx_corridor_analytics ON corridor_analytics (corridor_id, date, hour);
```

### 5.3 `weather_snapshots` — Weather Context

```sql
CREATE TABLE weather_snapshots (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    location        GEOMETRY(Point, 4326),
    zone_id         VARCHAR(50) REFERENCES zones(id),
    
    timestamp       TIMESTAMPTZ NOT NULL,
    temperature_c   FLOAT,
    humidity_pct    FLOAT,
    rainfall_mm     FLOAT,
    wind_speed_kmph FLOAT,
    visibility_m    FLOAT,
    condition       VARCHAR(50),
    
    UNIQUE(zone_id, timestamp)
);

CREATE INDEX idx_weather_time ON weather_snapshots (timestamp DESC);
CREATE INDEX idx_weather_zone ON weather_snapshots (zone_id, timestamp DESC);
```

---

## 6. AI Copilot Tables

### 6.1 `copilot_sessions` & `copilot_messages`

```sql
CREATE TABLE copilot_sessions (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID,
    title       VARCHAR(200),
    
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE copilot_messages (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id      UUID NOT NULL REFERENCES copilot_sessions(id) ON DELETE CASCADE,
    
    role            VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content         TEXT NOT NULL,
    
    -- RAG context
    retrieved_incidents UUID[] DEFAULT '{}',
    context_used    JSONB DEFAULT '{}',
    
    -- Model metadata
    model_used      VARCHAR(50),
    tokens_used     INTEGER,
    latency_ms      INTEGER,
    
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_copilot_messages_session ON copilot_messages (session_id, created_at);
```

---

## 7. Key Spatial Queries

### 7.1 Find Incidents Within Radius

```sql
-- Find all active incidents within 2km of a point
SELECT i.*, p.severity_score, p.resolution_time_minutes
FROM incidents i
LEFT JOIN predictions p ON p.incident_id = i.id
WHERE i.status IN ('open', 'active', 'dispatched')
  AND ST_DWithin(
      i.location::geography,
      ST_SetSRID(ST_MakePoint(77.5946, 12.9716), 4326)::geography,
      2000  -- meters
  )
ORDER BY ST_Distance(
    i.location::geography,
    ST_SetSRID(ST_MakePoint(77.5946, 12.9716), 4326)::geography
);
```

### 7.2 Hotspot Detection with DBSCAN

```sql
-- Cluster incidents using PostGIS ST_ClusterDBSCAN
SELECT 
    id,
    event_cause,
    ST_X(location) as lng,
    ST_Y(location) as lat,
    ST_ClusterDBSCAN(location, eps := 0.005, minpoints := 5) 
        OVER() AS cluster_id
FROM incidents
WHERE start_datetime >= NOW() - INTERVAL '7 days'
  AND status != 'closed';
```

### 7.3 Corridor Incident Density

```sql
-- Incidents per km on each corridor (last 30 days)
SELECT 
    c.name AS corridor,
    COUNT(i.id) AS incident_count,
    c.length_km,
    ROUND(COUNT(i.id)::numeric / NULLIF(c.length_km, 0), 2) AS incidents_per_km,
    ROUND(AVG(p.severity_score)::numeric, 3) AS avg_severity,
    ROUND(AVG(p.resolution_time_minutes)::numeric, 1) AS avg_resolution_min
FROM corridors c
LEFT JOIN incidents i ON i.corridor_id = c.id
    AND i.start_datetime >= NOW() - INTERVAL '30 days'
LEFT JOIN predictions p ON p.incident_id = i.id
GROUP BY c.id, c.name, c.length_km
ORDER BY incidents_per_km DESC;
```

### 7.4 Nearest Available Resource

```sql
-- Find closest available tow truck to an incident
SELECT 
    r.id,
    r.unit_name,
    r.type,
    ST_Distance(
        r.current_location::geography,
        (SELECT location FROM incidents WHERE id = $1)::geography
    ) / 1000 AS distance_km,
    ST_Distance(
        r.current_location::geography,
        (SELECT location FROM incidents WHERE id = $1)::geography
    ) / 1000 / 30 * 60 AS eta_minutes  -- Assume 30 km/h avg speed in BLR
FROM resources r
WHERE r.type = 'tow_truck'
  AND r.status = 'available'
ORDER BY r.current_location <-> (SELECT location FROM incidents WHERE id = $1)
LIMIT 5;
```

### 7.5 Zone Performance Dashboard

```sql
-- Zone-level KPIs
SELECT 
    z.name AS zone,
    COUNT(i.id) AS total_incidents,
    COUNT(i.id) FILTER (WHERE i.status IN ('open', 'active')) AS active_incidents,
    ROUND(AVG(i.duration_minutes)::numeric, 1) AS avg_duration_min,
    COUNT(i.id) FILTER (WHERE i.requires_road_closure) AS closure_count,
    ROUND(
        COUNT(i.id) FILTER (WHERE i.status = 'resolved' AND i.duration_minutes <= 60)::numeric /
        NULLIF(COUNT(i.id) FILTER (WHERE i.status = 'resolved'), 0) * 100, 1
    ) AS pct_resolved_within_1hr
FROM zones z
LEFT JOIN incidents i ON i.zone_id = z.id
    AND i.start_datetime >= NOW() - INTERVAL '30 days'
GROUP BY z.id, z.name
ORDER BY total_incidents DESC;
```

---

## 8. SQLAlchemy Models

```python
# app/models/incident.py
from sqlalchemy import Column, String, Boolean, Float, Integer, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from datetime import datetime
import uuid

from app.db.base import Base


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String(20), unique=True)
    
    # Classification
    event_type = Column(String(20), nullable=False)
    event_cause = Column(String(50), nullable=False)
    priority = Column(String(10), nullable=False, default="Medium")
    status = Column(String(20), nullable=False, default="open")
    
    # Geospatial
    location = Column(Geometry("POINT", srid=4326), nullable=False)
    end_location = Column(Geometry("POINT", srid=4326))
    address = Column(Text)
    end_address = Column(Text)
    
    # Road Impact
    requires_road_closure = Column(Boolean, default=False)
    affected_lanes = Column(Integer, default=0)
    
    # Temporal
    start_datetime = Column(DateTime(timezone=True), nullable=False)
    end_datetime = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    closed_at = Column(DateTime(timezone=True))
    
    # Vehicle
    vehicle_type = Column(String(30))
    vehicle_number = Column(String(20))
    cargo_material = Column(String(100))
    
    # Description
    description = Column(Text)
    
    # Foreign Keys
    corridor_id = Column(String(50), ForeignKey("corridors.id"))
    zone_id = Column(String(50), ForeignKey("zones.id"))
    junction_id = Column(String(50), ForeignKey("junctions.id"))
    police_station_id = Column(String(50), ForeignKey("police_stations.id"))
    
    # Metadata
    authenticated = Column(Boolean, default=False)
    metadata = Column(JSONB, default={})
    
    # Audit
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    predictions = relationship("Prediction", back_populates="incident", cascade="all, delete-orphan")
    timeline = relationship("IncidentTimeline", back_populates="incident", cascade="all, delete-orphan")
    resource_assignments = relationship("ResourceAssignment", back_populates="incident")
    
    corridor = relationship("Corridor", back_populates="incidents")
    zone = relationship("Zone", back_populates="incidents")
    junction = relationship("Junction", back_populates="incidents")
    police_station = relationship("PoliceStation", back_populates="incidents")

    def to_geojson(self):
        """Convert to GeoJSON Feature for map rendering."""
        from shapely import wkb
        point = wkb.loads(bytes(self.location.data))
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [point.x, point.y]
            },
            "properties": {
                "id": str(self.id),
                "event_type": self.event_type,
                "event_cause": self.event_cause,
                "priority": self.priority,
                "status": self.status,
                "description": self.description,
                "start_datetime": self.start_datetime.isoformat(),
                "requires_road_closure": self.requires_road_closure,
                "corridor": self.corridor_id,
            }
        }
```

---

## 9. Migration Strategy

### 9.1 Initial Data Load Script

```python
# scripts/load_dataset.py
import pandas as pd
from sqlalchemy import create_engine, text
from geoalchemy2 import WKTElement

def load_incidents(csv_path: str, db_url: str):
    """Load Astram dataset into PostgreSQL."""
    df = pd.read_csv(csv_path)
    engine = create_engine(db_url)
    
    with engine.begin() as conn:
        for _, row in df.iterrows():
            conn.execute(text("""
                INSERT INTO incidents (
                    external_id, event_type, location, address,
                    event_cause, requires_road_closure, start_datetime,
                    end_datetime, status, priority, description,
                    vehicle_type, vehicle_number, corridor_id,
                    police_station_id, zone_id, junction_id
                ) VALUES (
                    :ext_id, :event_type,
                    ST_SetSRID(ST_MakePoint(:lng, :lat), 4326),
                    :address, :cause, :closure, :start_dt,
                    :end_dt, :status, :priority, :description,
                    :veh_type, :veh_no, :corridor,
                    :police_station, :zone, :junction
                )
                ON CONFLICT (external_id) DO NOTHING
            """), {
                "ext_id": row["id"],
                "event_type": row["event_type"],
                "lat": row["latitude"],
                "lng": row["longitude"],
                "address": row.get("address"),
                "cause": row["event_cause"],
                "closure": row["requires_road_closure"] == "TRUE",
                "start_dt": row["start_datetime"],
                "end_dt": row.get("end_datetime") if row.get("end_datetime") != "NULL" else None,
                "status": row["status"],
                "priority": row["priority"],
                "description": row.get("description"),
                "veh_type": row.get("veh_type"),
                "veh_no": row.get("veh_no"),
                "corridor": normalize_corridor(row.get("corridor")),
                "police_station": normalize_station(row.get("police_station")),
                "zone": row.get("zone") if row.get("zone") else None,
                "junction": row.get("junction") if row.get("junction") else None,
            })
    
    print(f"Loaded {len(df)} incidents into PostgreSQL")

def normalize_corridor(raw: str) -> str:
    """Normalize corridor names to IDs."""
    if not raw or raw == "Non-corridor":
        return "non_corridor"
    return raw.lower().replace(" ", "_")

def normalize_station(raw: str) -> str:
    """Normalize police station names to IDs."""
    if not raw:
        return None
    return raw.lower().replace(" ", "_")
```

### 9.2 Alembic Migration

```python
# alembic/versions/001_initial_schema.py
"""Initial schema with PostGIS

Revision ID: 001
"""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Create tables in dependency order
    op.create_table('corridors', ...)
    op.create_table('zones', ...)
    op.create_table('junctions', ...)
    op.create_table('police_stations', ...)
    op.create_table('incidents', ...)
    op.create_table('predictions', ...)
    # ... etc

def downgrade():
    op.drop_table('predictions')
    op.drop_table('incidents')
    # ... reverse order
```

---

## 10. Performance Optimization

### 10.1 Table Partitioning (Production)

```sql
-- Partition incidents by month for production scale
CREATE TABLE incidents_partitioned (
    LIKE incidents INCLUDING ALL
) PARTITION BY RANGE (start_datetime);

CREATE TABLE incidents_2024_01 PARTITION OF incidents_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
CREATE TABLE incidents_2024_02 PARTITION OF incidents_partitioned
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
-- ... etc
```

### 10.2 Materialized Views

```sql
-- Pre-computed daily statistics (refresh every hour)
CREATE MATERIALIZED VIEW mv_daily_stats AS
SELECT 
    DATE(start_datetime) AS incident_date,
    event_cause,
    corridor_id,
    zone_id,
    COUNT(*) AS incident_count,
    AVG(duration_minutes) AS avg_duration,
    COUNT(*) FILTER (WHERE requires_road_closure) AS closure_count,
    COUNT(*) FILTER (WHERE priority = 'High') AS high_priority_count
FROM incidents
GROUP BY DATE(start_datetime), event_cause, corridor_id, zone_id;

CREATE UNIQUE INDEX idx_mv_daily_stats 
    ON mv_daily_stats (incident_date, event_cause, corridor_id, zone_id);

-- Refresh command
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_stats;
```

### 10.3 Connection Pooling

```python
# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    "postgresql://namma:traffic@localhost:5432/nammatraffic",
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

---

## 11. Redis Cache Schema

```python
# Redis key patterns for caching

REDIS_KEYS = {
    # Active incidents GeoJSON (refreshed every 30s)
    "incidents:active:geojson": "GeoJSON FeatureCollection",
    
    # Dashboard counters (refreshed every 10s)
    "dashboard:counters": {
        "total_active": int,
        "by_priority": {"High": int, "Medium": int, "Low": int},
        "by_cause": {"vehicle_breakdown": int, ...},
        "by_zone": {...},
    },
    
    # Corridor status (refreshed every 60s)
    "corridor:{corridor_id}:status": {
        "active_incidents": int,
        "avg_severity": float,
        "has_closure": bool,
    },
    
    # User session
    "session:{session_id}": {"user_id": str, "role": str, ...},
    
    # Rate limiting
    "ratelimit:{ip}:{endpoint}": int,  # TTL: 60s
    
    # ML prediction cache
    "prediction:{incident_id}": {...},  # TTL: 300s
}
```

---

*This schema is designed for rapid development while maintaining clear paths to production scale. PostGIS spatial indexes and pre-computed materialized views ensure the map and analytics dashboards remain responsive even with growing data.*
