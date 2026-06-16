# GIS Architecture — Geospatial Intelligence Layer

## Overview

The GIS layer transforms raw lat/long coordinates from 8,173 Bengaluru traffic incidents into actionable spatial intelligence: hotspot detection, risk maps, cluster analysis, and diversion routing.

---

## Tech Stack

| Component | Technology |
|---|---|
| Map Rendering | MapLibre GL JS (open-source, no API key required) |
| Tile Server | OpenStreetMap / Mapbox (free tier) |
| Spatial DB | PostGIS extension on PostgreSQL |
| Server-side Geo | Python: shapely, geopandas, h3, scikit-learn (KMeans/DBSCAN) |
| Client-side Geo | Turf.js (browser-side spatial ops) |
| Geocoding | Nominatim (OSM, free) |

---

## Spatial Data Profile (from Audit)

| Metric | Value |
|---|---|
| Centroid | 12.9871°N, 77.5960°E (Central Bengaluru) |
| Bounding Box | (12.80, 77.31) → (13.27, 77.77) |
| Spatial Extent | ~47km × 51km |
| Corridors | 22 named corridors + "Non-corridor" |
| Zones | East, West, North, South, Central (5 GBA zones) |
| Junctions | ~200+ named junctions (42% coverage) |

---

## Layer 1: Incident Heatmap

Real-time kernel density estimation of active and historical incidents.

```javascript
// MapLibre GL JS heatmap layer
map.addLayer({
  id: 'incident-heat',
  type: 'heatmap',
  source: 'incidents',
  paint: {
    'heatmap-weight': ['interpolate', ['linear'], ['get', 'severity_score'], 0, 0, 1, 1],
    'heatmap-intensity': ['interpolate', ['linear'], ['zoom'], 0, 1, 15, 3],
    'heatmap-radius': ['interpolate', ['linear'], ['zoom'], 0, 5, 15, 30],
    'heatmap-color': [
      'interpolate', ['linear'], ['heatmap-density'],
      0, 'rgba(0,0,255,0)', 0.2, '#2196F3', 0.4, '#4CAF50',
      0.6, '#FFC107', 0.8, '#FF5722', 1, '#D32F2F'
    ]
  }
});
```

---

## Layer 2: Hotspot Clusters (DBSCAN)

Identify persistent incident hotspots using density-based clustering.

```python
from sklearn.cluster import DBSCAN
import numpy as np

# Convert to radians for haversine
coords_rad = np.radians(df[['latitude', 'longitude']].values)

# eps = 500m in radians, min 5 incidents to form a cluster
clustering = DBSCAN(
    eps=500 / 6371000,  # 500m radius
    min_samples=5,
    metric='haversine'
).fit(coords_rad)

df['hotspot_cluster'] = clustering.labels_
n_hotspots = len(set(clustering.labels_)) - 1  # Exclude noise (-1)
```

---

## Layer 3: H3 Hexagonal Grid Risk Map

Use Uber's H3 hexagonal indexing for uniform spatial binning.

```python
import h3

# Resolution 8 ≈ 460m edge length — good for city blocks
df['h3_index'] = df.apply(
    lambda r: h3.latlng_to_cell(r['latitude'], r['longitude'], 8), axis=1
)

# Incident density per hex
hex_risk = df.groupby('h3_index').agg(
    incident_count=('id', 'count'),
    closure_rate=('requires_road_closure', 'mean'),
    high_priority_rate=('is_high_priority', 'mean')
).reset_index()

# Risk score = weighted combination
hex_risk['risk_score'] = (
    0.5 * hex_risk['incident_count'] / hex_risk['incident_count'].max() +
    0.3 * hex_risk['closure_rate'] +
    0.2 * hex_risk['high_priority_rate']
)
```

---

## Layer 4: Corridor Risk Scoring

22 named corridors with per-corridor risk metrics.

```python
corridor_risk = df.groupby('corridor').agg(
    total_incidents=('id', 'count'),
    closure_rate=('requires_road_closure', 'mean'),
    high_priority_pct=('is_high_priority', 'mean'),
    avg_resolution_hours=('resolution_hours', 'median'),
    breakdown_pct=('is_breakdown', 'mean')
).sort_values('total_incidents', ascending=False)
```

Top corridors from audit:
1. Non-corridor (38.2%) — scattered locations
2. Mysore Road (9.1%)
3. Bellary Road 1 (7.5%)
4. Tumkur Road (7.0%)

---

## Layer 5: Diversion Route Suggestion

When a road closure is predicted, suggest alternative routes using the road network.

### Approach
1. Identify the affected corridor/junction from the incident
2. Look up pre-computed diversion routes for that corridor
3. Fall back to OSM-based routing via OSRM (Open Source Routing Machine)

```python
# Pre-computed diversion table (built from domain knowledge + OSM)
DIVERSIONS = {
    'Bellary Road 1': {
        'primary': 'Sankey Road → Palace Road',
        'secondary': 'Mekhri Circle → Jayamahal Road',
        'estimated_delay_mins': 12
    },
    'Mysore Road': {
        'primary': 'Chord Road → Magadi Road',
        'secondary': 'NICE Road → Kanakapura Road',
        'estimated_delay_mins': 18
    },
    # ... for all 22 corridors
}
```

---

## Layer 6: Spatial-Temporal Risk Forecast

Predict which H3 hexagons are at highest risk in the next 1/4/12 hours.

```
Features per hex per time window:
- historical incident count (same hour, same day_of_week)
- historical closure rate
- rolling 7-day incident count
- corridor risk score
- nearby active incidents (within 2km)

Model: LightGBM regressor predicting incident_count per hex per 4h window
```

---

## Map UI Components

| Component | Purpose |
|---|---|
| **Incident Markers** | Color-coded pins (red=High, yellow=Low, blue=Active) |
| **Heatmap Toggle** | Switch between point view and density view |
| **Cluster View** | DBSCAN clusters as polygon boundaries |
| **Hex Grid** | H3 hexagons colored by risk score |
| **Corridor Highlight** | Click corridor name → highlight on map |
| **Radius Search** | Draw circle → find all incidents within radius |
| **Time Slider** | Animate incidents over time (hourly/daily) |
