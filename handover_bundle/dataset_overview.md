# 📊 Dataset Overview Report

## Astram Event Data — Bengaluru Traffic Incidents

**File**: `Astram event data_anonymized - Astram event data_anonymizedb40ac87.csv`

**Rows**: 8,173
**Columns**: 46
**Memory Usage**: 12.6 MB

## Column Schema

| # | Column Name | Dtype | Non-Null Count | Null Count | Null % | Sample Value |
|---|------------|-------|---------------|-----------|--------|-------------|
| 1 | `id` | str | 8,173 | 0 | 0.0% | FKID000000 |
| 2 | `event_type` | str | 8,173 | 0 | 0.0% | unplanned |
| 3 | `latitude` | float64 | 8,173 | 0 | 0.0% | 13.0400041 |
| 4 | `longitude` | float64 | 8,173 | 0 | 0.0% | 77.5180991 |
| 5 | `endlatitude` | float64 | 8,004 | 169 | 2.1% | 0.0 |
| 6 | `endlongitude` | float64 | 8,004 | 169 | 2.1% | 0.0 |
| 7 | `address` | str | 8,170 | 3 | 0.0% | Mumbai Bengaluru Highway, Jalahalli Cross Junction, Peenya,  |
| 8 | `end_address` | str | 687 | 7,486 | 91.6% | Sankey Road, Palace Orchard Upper, Sadashiva Nagar, Bengalur |
| 9 | `event_cause` | str | 8,173 | 0 | 0.0% | vehicle_breakdown |
| 10 | `requires_road_closure` | bool | 8,173 | 0 | 0.0% | False |
| 11 | `start_datetime` | datetime64[us, UTC] | 8,057 | 116 | 1.4% | 2024-03-07 17:01:48.111000+00:00 |
| 12 | `end_datetime` | datetime64[us, UTC] | 475 | 7,698 | 94.2% | 2024-02-12 14:05:46+00:00 |
| 13 | `status` | str | 8,173 | 0 | 0.0% | closed |
| 14 | `authenticated` | str | 8,173 | 0 | 0.0% | yes |
| 15 | `modified_datetime` | datetime64[us, UTC] | 8,173 | 0 | 0.0% | 2024-03-07 19:35:47.871698+00:00 |
| 16 | `map_file` | float64 | 0 | 8,173 | 100.0% | N/A |
| 17 | `direction` | str | 43 | 8,130 | 99.5% | north |
| 18 | `description` | str | 6,813 | 1,360 | 16.6% | s m circle in coming  man track |
| 19 | `veh_type` | str | 4,887 | 3,286 | 40.2% | lcv |
| 20 | `veh_no` | str | 4,886 | 3,287 | 40.2% | FKN00GL0000 |
| 21 | `corridor` | str | 8,153 | 20 | 0.2% | Tumkur Road |
| 22 | `priority` | str | 8,171 | 2 | 0.0% | High |
| 23 | `cargo_material` | str | 276 | 7,897 | 96.6% | goods |
| 24 | `reason_breakdown` | str | 276 | 7,897 | 96.6% | clutch plate problem |
| 25 | `age_of_truck` | float64 | 276 | 7,897 | 96.6% | 2021.0 |
| 26 | `created_date` | datetime64[us, UTC] | 8,171 | 2 | 0.0% | 2024-03-07 17:03:51.164032+00:00 |
| 27 | `route_path` | str | 137 | 8,036 | 98.3% | [] |
| 28 | `client_id` | int64 | 8,173 | 0 | 0.0% | 1 |
| 29 | `created_by_id` | str | 8,171 | 2 | 0.0% | FKUSR00000 |
| 30 | `last_modified_by_id` | str | 8,170 | 3 | 0.0% | FKUSR00001 |
| 31 | `assigned_to_police_id` | str | 128 | 8,045 | 98.4% | FKUSR00005 |
| 32 | `citizen_accident_id` | str | 128 | 8,045 | 98.4% | FKUSR00006 |
| 33 | `comment` | float64 | 0 | 8,173 | 100.0% | N/A |
| 34 | `police_station` | str | 8,173 | 0 | 0.0% | Peenya |
| 35 | `meta_data` | float64 | 0 | 8,173 | 100.0% | N/A |
| 36 | `kgid` | str | 7,914 | 259 | 3.2% | FKKG000000 |
| 37 | `resolved_at_address` | str | 74 | 8,099 | 99.1% | 19th Main Road, Heavie Halcyon, Agara, HSR Layout, Bengaluru |
| 38 | `resolved_at_latitude` | float64 | 74 | 8,099 | 99.1% | 12.9218755 |
| 39 | `resolved_at_longitude` | float64 | 74 | 8,099 | 99.1% | 77.6451585 |
| 40 | `closed_by_id` | str | 3,141 | 5,032 | 61.6% | FKUSR00003 |
| 41 | `closed_datetime` | datetime64[us, UTC] | 3,141 | 5,032 | 61.6% | 2024-01-30 04:56:03.281509+00:00 |
| 42 | `resolved_by_id` | str | 74 | 8,099 | 99.1% | FKUSR00002 |
| 43 | `resolved_datetime` | datetime64[us, UTC] | 74 | 8,099 | 99.1% | 2024-01-30 04:17:46.828355+00:00 |
| 44 | `gba_identifier` | str | 3,444 | 4,729 | 57.9% | Bengaluru Central Corporation |
| 45 | `zone` | str | 3,444 | 4,729 | 57.9% | Central Zone 2 |
| 46 | `junction` | str | 2,510 | 5,663 | 69.3% | UrvashiJunction |

## Data Types Summary

- **str**: 28 columns
- **float64**: 10 columns
- **datetime64[us, UTC]**: 6 columns
- **bool**: 1 columns
- **int64**: 1 columns

## First 5 Row IDs

```
ID: FKID000000, Type: unplanned, Status: closed, Cause: vehicle_breakdown
ID: FKID000001, Type: unplanned, Status: resolved, Cause: vehicle_breakdown
ID: FKID000002, Type: unplanned, Status: closed, Cause: others
ID: FKID000003, Type: unplanned, Status: closed, Cause: tree_fall
ID: FKID000004, Type: unplanned, Status: closed, Cause: vehicle_breakdown
```

## Key Column Distributions (Preview)

### `event_type` (top values)

| Value | Count | % |
|-------|-------|---|
| unplanned | 7,706 | 94.3% |
| planned | 467 | 5.7% |

### `status` (top values)

| Value | Count | % |
|-------|-------|---|
| closed | 7,095 | 86.8% |
| active | 1,007 | 12.3% |
| resolved | 71 | 0.9% |

### `event_cause` (top values)

| Value | Count | % |
|-------|-------|---|
| vehicle_breakdown | 4,896 | 59.9% |
| others | 638 | 7.8% |
| pot_holes | 537 | 6.6% |
| construction | 480 | 5.9% |
| water_logging | 458 | 5.6% |
| accident | 365 | 4.5% |
| tree_fall | 284 | 3.5% |
| road_conditions | 170 | 2.1% |
| congestion | 136 | 1.7% |
| public_event | 84 | 1.0% |

### `priority` (top values)

| Value | Count | % |
|-------|-------|---|
| High | 5,030 | 61.5% |
| Low | 3,141 | 38.4% |
| nan | 2 | 0.0% |

### `requires_road_closure` (top values)

| Value | Count | % |
|-------|-------|---|
| False | 7,497 | 91.7% |
| True | 676 | 8.3% |

### `authenticated` (top values)

| Value | Count | % |
|-------|-------|---|
| yes | 7,166 | 87.7% |
| no | 1,007 | 12.3% |
