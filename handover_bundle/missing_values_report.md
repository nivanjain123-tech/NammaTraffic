# 🕳️ Missing Values Report

**Total Records**: 8,173

**Total Cells**: 375,958
**Missing Cells**: 170,008
**Overall Missing Rate**: 45.22%

## Missing Values by Column

| Column | Non-Null | Missing | Missing % | Severity |
|--------|---------|---------|-----------|----------|
| `meta_data` | 0 | 8,173 | 100.0% | 🔴 Critical |
| `comment` | 0 | 8,173 | 100.0% | 🔴 Critical |
| `map_file` | 0 | 8,173 | 100.0% | 🔴 Critical |
| `direction` | 43 | 8,130 | 99.5% | 🔴 Critical |
| `resolved_at_longitude` | 74 | 8,099 | 99.1% | 🔴 Critical |
| `resolved_at_latitude` | 74 | 8,099 | 99.1% | 🔴 Critical |
| `resolved_at_address` | 74 | 8,099 | 99.1% | 🔴 Critical |
| `resolved_by_id` | 74 | 8,099 | 99.1% | 🔴 Critical |
| `resolved_datetime` | 74 | 8,099 | 99.1% | 🔴 Critical |
| `citizen_accident_id` | 128 | 8,045 | 98.4% | 🔴 Critical |
| `assigned_to_police_id` | 128 | 8,045 | 98.4% | 🔴 Critical |
| `route_path` | 137 | 8,036 | 98.3% | 🔴 Critical |
| `cargo_material` | 276 | 7,897 | 96.6% | 🔴 Critical |
| `age_of_truck` | 276 | 7,897 | 96.6% | 🔴 Critical |
| `reason_breakdown` | 276 | 7,897 | 96.6% | 🔴 Critical |
| `end_datetime` | 475 | 7,698 | 94.2% | 🔴 Critical |
| `end_address` | 687 | 7,486 | 91.6% | 🔴 Critical |
| `junction` | 2,510 | 5,663 | 69.3% | 🔴 Critical |
| `closed_datetime` | 3,141 | 5,032 | 61.6% | 🔴 Critical |
| `closed_by_id` | 3,141 | 5,032 | 61.6% | 🔴 Critical |
| `zone` | 3,444 | 4,729 | 57.9% | 🔴 Critical |
| `gba_identifier` | 3,444 | 4,729 | 57.9% | 🔴 Critical |
| `veh_no` | 4,886 | 3,287 | 40.2% | 🟡 Moderate |
| `veh_type` | 4,887 | 3,286 | 40.2% | 🟡 Moderate |
| `description` | 6,813 | 1,360 | 16.6% | 🟡 Moderate |
| `kgid` | 7,914 | 259 | 3.2% | 🟢 Good |
| `endlatitude` | 8,004 | 169 | 2.1% | 🟢 Good |
| `endlongitude` | 8,004 | 169 | 2.1% | 🟢 Good |
| `start_datetime` | 8,057 | 116 | 1.4% | 🟢 Good |
| `corridor` | 8,153 | 20 | 0.2% | 🟢 Good |
| `address` | 8,170 | 3 | 0.0% | 🟢 Good |
| `last_modified_by_id` | 8,170 | 3 | 0.0% | 🟢 Good |
| `created_by_id` | 8,171 | 2 | 0.0% | 🟢 Good |
| `created_date` | 8,171 | 2 | 0.0% | 🟢 Good |
| `priority` | 8,171 | 2 | 0.0% | 🟢 Good |
| `latitude` | 8,173 | 0 | 0.0% | 🟢 Good |
| `longitude` | 8,173 | 0 | 0.0% | 🟢 Good |
| `requires_road_closure` | 8,173 | 0 | 0.0% | 🟢 Good |
| `event_cause` | 8,173 | 0 | 0.0% | 🟢 Good |
| `police_station` | 8,173 | 0 | 0.0% | 🟢 Good |
| `status` | 8,173 | 0 | 0.0% | 🟢 Good |
| `client_id` | 8,173 | 0 | 0.0% | 🟢 Good |
| `authenticated` | 8,173 | 0 | 0.0% | 🟢 Good |
| `modified_datetime` | 8,173 | 0 | 0.0% | 🟢 Good |
| `event_type` | 8,173 | 0 | 0.0% | 🟢 Good |
| `id` | 8,173 | 0 | 0.0% | 🟢 Good |

## Missing Value Categories

### 🟢 Complete Columns (0% missing): 11
```
latitude, longitude, requires_road_closure, event_cause, police_station, status, client_id, authenticated, modified_datetime, event_type, id
```

### 🟡 Low Missing (<5%): 10
```
kgid, endlatitude, endlongitude, start_datetime, corridor, address, last_modified_by_id, created_by_id, created_date, priority
```

### 🟠 Moderate Missing (5-50%): 3
```
veh_no, veh_type, description
```

### 🔴 High Missing (>50%): 22
```
meta_data, comment, map_file, direction, resolved_at_longitude, resolved_at_latitude, resolved_at_address, resolved_by_id, resolved_datetime, citizen_accident_id, assigned_to_police_id, route_path, cargo_material, age_of_truck, reason_breakdown, end_datetime, end_address, junction, closed_datetime, closed_by_id, zone, gba_identifier
```

## Row-Level Missing Analysis

- **Max missing columns per row**: 29
- **Mean missing columns per row**: 20.8
- **Median missing columns per row**: 21
- **Rows with 0 missing**: 0
- **Rows with >10 missing**: 8,173
- **Rows with >20 missing**: 4,438

## Missing Together Analysis

Columns that tend to be missing together (potential structural patterns):

- **End location group** (endlatitude, endlongitude, end_address): all-missing=169 rows, any-missing=7,486 rows
- **Vehicle group** (veh_type, veh_no): all-missing=3,286 rows, any-missing=3,287 rows
- **Resolution group** (resolved_at_address, resolved_at_latitude, resolved_at_longitude, resolved_datetime): all-missing=8,099 rows, any-missing=8,099 rows
- **Closure group** (closed_datetime, closed_by_id): all-missing=5,032 rows, any-missing=5,032 rows
- **Geo admin group** (zone, junction, gba_identifier): all-missing=4,415 rows, any-missing=5,977 rows
- **Breakdown-specific** (cargo_material, reason_breakdown, age_of_truck): all-missing=7,897 rows, any-missing=7,897 rows