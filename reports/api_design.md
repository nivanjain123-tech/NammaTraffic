# API Design — RESTful Endpoints

## Base URL
```
https://api.gridlock.bengaluru.dev/v1
```

## Authentication
```
Authorization: Bearer <jwt_token>
```

---

## 1. Incidents API

### GET /incidents
List all incidents with filtering, pagination, and sorting.

**Query Parameters:**
| Param | Type | Example |
|---|---|---|
| status | string | `active`, `closed`, `resolved` |
| priority | string | `High`, `Low` |
| event_cause | string | `vehicle_breakdown`, `accident` |
| corridor | string | `Bellary Road 1` |
| zone | string | `East` |
| from_date | ISO8601 | `2024-01-01T00:00:00Z` |
| to_date | ISO8601 | `2024-03-31T23:59:59Z` |
| lat, lon, radius_km | float | `12.97,77.59,5` |
| page, per_page | int | `1,50` |

**Response:**
```json
{
  "total": 1007,
  "page": 1,
  "incidents": [
    {
      "id": "FKID000100",
      "event_type": "unplanned",
      "event_cause": "vehicle_breakdown",
      "priority": "High",
      "status": "active",
      "location": { "lat": 12.9718, "lon": 77.5946, "address": "MG Road..." },
      "corridor": "MG Road",
      "start_datetime": "2024-03-07T17:01:48Z",
      "predictions": {
        "severity": "High",
        "road_closure_prob": 0.12,
        "estimated_resolution_mins": 45,
        "resources": { "officers": 2, "barricades": 0, "tow_truck": true }
      }
    }
  ]
}
```

### GET /incidents/{id}
Get full incident details including predictions and similar incidents.

### POST /incidents
Create a new incident (triggers ML prediction pipeline).

**Request Body:**
```json
{
  "event_type": "unplanned",
  "event_cause": "vehicle_breakdown",
  "latitude": 12.9718,
  "longitude": 77.5946,
  "address": "MG Road, near Trinity Circle",
  "description": "Heavy vehicle breakdown blocking left lane",
  "veh_type": "heavy_vehicle",
  "corridor": "MG Road"
}
```

**Response:** Enriched incident with all predictions (same as GET response).

### PATCH /incidents/{id}
Update incident status, add resolution details.

---

## 2. Predictions API

### POST /predict/enrich
Send an incident payload, receive all ML predictions without saving.

**Request:** Same as POST /incidents
**Response:**
```json
{
  "severity": { "prediction": "High", "confidence": 0.87 },
  "road_closure": { "prediction": false, "probability": 0.12 },
  "resolution_time": { "prediction_mins": 45, "bin": "30min-2h" },
  "event_cause": { "prediction": "vehicle_breakdown", "confidence": 0.92 },
  "resources": { "officers": 2, "barricades": 0, "tow_truck": true },
  "similar_incidents": [
    { "id": "FKID000050", "similarity": 0.94, "resolution_mins": 38 }
  ]
}
```

### GET /predict/risk-map
Get current spatial risk scores.

**Query:** `?resolution=8&hours_ahead=4`
**Response:** Array of H3 hexagons with risk scores.

---

## 3. Analytics API

### GET /analytics/corridors
Corridor-level statistics.

### GET /analytics/hotspots
DBSCAN cluster centroids with incident counts.

### GET /analytics/trends
Time-series trends (daily/weekly/monthly incident counts).

### GET /analytics/performance
Resolution time benchmarks by zone, corridor, cause.

---

## 4. Search API

### POST /search/similar
Find similar historical incidents.

**Request:**
```json
{
  "event_cause": "tree_fall",
  "latitude": 12.97,
  "longitude": 77.59,
  "hour": 17,
  "corridor": "Bellary Road 1",
  "top_k": 5
}
```

---

## 5. Copilot API

### POST /copilot/chat
Natural language query interface.

**Request:**
```json
{
  "message": "What is the expected impact of a vehicle breakdown on ORR at 6 PM?",
  "session_id": "abc123"
}
```

**Response:**
```json
{
  "response": "Based on 312 historical vehicle breakdowns on ORR during evening peak hours (5-8 PM), the expected impact is:\n\n- **Severity**: High (78% of similar incidents)\n- **Road Closure**: Unlikely (4.3% probability)\n- **Resolution Time**: ~45 minutes (median)\n- **Recommended**: Deploy 2 officers + 1 tow truck\n\nThe most similar incident was FKID001234 on Feb 15, 2024, which was resolved in 38 minutes.",
  "sources": ["FKID001234", "FKID002345"],
  "actions": [
    { "label": "Show on map", "action": "navigate", "params": { "lat": 12.97, "lon": 77.59 } },
    { "label": "Deploy resources", "action": "dispatch", "params": { "officers": 2 } }
  ]
}
```

---

## 6. WebSocket — Real-time Updates

### WS /ws/incidents
Live incident feed for the command center dashboard.

```javascript
const ws = new WebSocket('wss://api.gridlock.bengaluru.dev/v1/ws/incidents');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // data.type: 'new_incident' | 'status_update' | 'prediction_update'
  updateMap(data);
};
```
