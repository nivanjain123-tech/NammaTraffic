# 📋 Feature Catalog

Each column categorized with type, unique values, and distribution.

## Feature Classification Summary

| Category | Count | Columns |
|----------|-------|---------|
| Categorical | 16 | event_type, event_cause, requires_road_closure, status, authenticated, direction, veh_type, corridor, priority, cargo_material, reason_breakdown, police_station, zone, junction, gba_identifier, map_file |
| Numerical | 7 | latitude, longitude, endlatitude, endlongitude, resolved_at_latitude, resolved_at_longitude, age_of_truck |
| Temporal | 6 | start_datetime, end_datetime, modified_datetime, created_date, closed_datetime, resolved_datetime |
| Text/Free-form | 7 | address, end_address, description, comment, resolved_at_address, route_path, meta_data |
| Identifier | 10 | id, veh_no, client_id, created_by_id, last_modified_by_id, assigned_to_police_id, citizen_accident_id, closed_by_id, resolved_by_id, kgid |

---
## Detailed Feature Analysis

### 🏷️ Categorical Features

#### `event_type`
- **Unique values**: 2
- **Non-null**: 8,173 (100.0%)
- **Top values**:

| Value | Count | % |
|-------|-------|---|
| unplanned | 7,706 | 94.3% |
| planned | 467 | 5.7% |

#### `event_cause`
- **Unique values**: 17
- **Non-null**: 8,173 (100.0%)
- **Top values**:

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
| procession | 72 | 0.9% |
| vip_movement | 20 | 0.2% |
| protest | 15 | 0.2% |
| Debris | 12 | 0.1% |
| test_demo | 3 | 0.0% |

#### `requires_road_closure`
- **Unique values**: 2
- **Non-null**: 8,173 (100.0%)
- **Top values**:

| Value | Count | % |
|-------|-------|---|
| False | 7,497 | 91.7% |
| True | 676 | 8.3% |

#### `status`
- **Unique values**: 3
- **Non-null**: 8,173 (100.0%)
- **Top values**:

| Value | Count | % |
|-------|-------|---|
| closed | 7,095 | 86.8% |
| active | 1,007 | 12.3% |
| resolved | 71 | 0.9% |

#### `authenticated`
- **Unique values**: 2
- **Non-null**: 8,173 (100.0%)
- **Top values**:

| Value | Count | % |
|-------|-------|---|
| yes | 7,166 | 87.7% |
| no | 1,007 | 12.3% |

#### `direction`
- **Unique values**: 8
- **Non-null**: 43 (0.5%)
- **Top values**:

| Value | Count | % |
|-------|-------|---|
| nan | 8,130 | 99.5% |
| south_west | 12 | 0.1% |
| north_west | 10 | 0.1% |
| west | 8 | 0.1% |
| south | 7 | 0.1% |
| north | 2 | 0.0% |
| north_east | 2 | 0.0% |
| east | 1 | 0.0% |
| south_east | 1 | 0.0% |

#### `veh_type`
- **Unique values**: 10
- **Non-null**: 4,887 (59.8%)
- **Top values**:

| Value | Count | % |
|-------|-------|---|
| nan | 3,286 | 40.2% |
| bmtc_bus | 1,466 | 17.9% |
| heavy_vehicle | 965 | 11.8% |
| lcv | 678 | 8.3% |
| others | 449 | 5.5% |
| private_bus | 359 | 4.4% |
| private_car | 345 | 4.2% |
| truck | 276 | 3.4% |
| ksrtc_bus | 217 | 2.7% |
| taxi | 95 | 1.2% |
| auto | 37 | 0.5% |

#### `corridor`
- **Unique values**: 22
- **Non-null**: 8,153 (99.8%)
- **Top values**:

| Value | Count | % |
|-------|-------|---|
| Non-corridor | 3,124 | 38.2% |
| Mysore Road | 743 | 9.1% |
| Bellary Road 1 | 610 | 7.5% |
| Tumkur Road | 458 | 5.6% |
| Bellary Road 2 | 379 | 4.6% |
| Hosur Road | 298 | 3.6% |
| ORR North 1 | 275 | 3.4% |
| Old Madras Road | 263 | 3.2% |
| Magadi Road | 245 | 3.0% |
| ORR East 1 | 244 | 3.0% |
| ORR North 2 | 235 | 2.9% |
| Bannerghata Road | 209 | 2.6% |
| ORR East 2 | 187 | 2.3% |
| West of Chord Road | 174 | 2.1% |
| ORR West 1 | 168 | 2.1% |

#### `priority`
- **Unique values**: 2
- **Non-null**: 8,171 (100.0%)
- **Top values**:

| Value | Count | % |
|-------|-------|---|
| High | 5,030 | 61.5% |
| Low | 3,141 | 38.4% |
| nan | 2 | 0.0% |

#### `cargo_material`
- **Unique values**: 138
- **Non-null**: 276 (3.4%)
- **Top values**:

| Value | Count | % |
|-------|-------|---|
| nan | 7,897 | 96.6% |
| Goods | 23 | 0.3% |
| goods | 20 | 0.2% |
| Goods carried | 18 | 0.2% |
| goods carried | 13 | 0.2% |
| Yes | 11 | 0.1% |
| No | 9 | 0.1% |
| Materials | 8 | 0.1% |
| empty | 7 | 0.1% |
| Empty | 7 | 0.1% |
| goods carrier | 5 | 0.1% |
| materials | 5 | 0.1% |
| emty | 5 | 0.1% |
| Material | 5 | 0.1% |
| Cement | 3 | 0.0% |

#### `reason_breakdown`
- **Unique values**: 193
- **Non-null**: 276 (3.4%)
- **Top values**:

| Value | Count | % |
|-------|-------|---|
| nan | 7,897 | 96.6% |
| Starting problem | 22 | 0.3% |
| starting problem | 11 | 0.1% |
| Breakdown | 8 | 0.1% |
| breakdown | 6 | 0.1% |
| break down | 5 | 0.1% |
| Puncher | 5 | 0.1% |
| Tire burst | 4 | 0.0% |
| mechanical problem | 4 | 0.0% |
| Tyre brust | 4 | 0.0% |
| Diesel empty | 3 | 0.0% |
| Gear problem | 3 | 0.0% |
| brek down | 3 | 0.0% |
| Tyre puncture | 3 | 0.0% |
| clutch plate problem | 2 | 0.0% |

#### `police_station`
- **Unique values**: 54
- **Non-null**: 8,173 (100.0%)
- **Top values**:

| Value | Count | % |
|-------|-------|---|
| Yelahanka | 377 | 4.6% |
| HAL Old Airport | 361 | 4.4% |
| Sadashivanagar | 302 | 3.7% |
| Byatarayanapura | 297 | 3.6% |
| Halasuru Gate | 297 | 3.6% |
| Yeshwanthpura | 280 | 3.4% |
| Hennuru | 276 | 3.4% |
| Kodigehalli | 272 | 3.3% |
| Banaswadi | 245 | 3.0% |
| K.R. Pura | 228 | 2.8% |
| Kamakshipalya | 224 | 2.7% |
| No Police Station | 219 | 2.7% |
| Cubbon Park | 212 | 2.6% |
| Jalahalli | 197 | 2.4% |
| Chamarajpet | 192 | 2.3% |

#### `zone`
- **Unique values**: 10
- **Non-null**: 3,444 (42.1%)
- **Top values**:

| Value | Count | % |
|-------|-------|---|
| nan | 4,729 | 57.9% |
| Central Zone 2 | 623 | 7.6% |
| West Zone 1 | 433 | 5.3% |
| North Zone 2 | 413 | 5.1% |
| West Zone 2 | 358 | 4.4% |
| South Zone 2 | 354 | 4.3% |
| North Zone 1 | 318 | 3.9% |
| Central Zone 1 | 269 | 3.3% |
| East Zone 1 | 253 | 3.1% |
| South Zone 1 | 233 | 2.9% |
| East Zone 2 | 190 | 2.3% |

#### `junction`
- **Unique values**: 294
- **Non-null**: 2,510 (30.7%)
- **Top values**:

| Value | Count | % |
|-------|-------|---|
| nan | 5,663 | 69.3% |
| MekhriCircle | 64 | 0.8% |
| AyyappaTempleJunc | 49 | 0.6% |
| SatteliteBusStandJunc | 43 | 0.5% |
| YeshwanthpuraCircle | 38 | 0.5% |
| YelhankaCircle | 34 | 0.4% |
| SilkBoardJunc | 33 | 0.4% |
| toll gate mysore road | 33 | 0.4% |
| JalahalliCross(SM Circle) | 32 | 0.4% |
| Nagavara-ORR Junction | 32 | 0.4% |
| K R Circle | 31 | 0.4% |
| KIMCO Junction | 31 | 0.4% |
| VeerannapalyaJunction(BEL,HO) | 30 | 0.4% |
| TownhallJunction | 30 | 0.4% |
| HesaraghattaJunction | 30 | 0.4% |

#### `gba_identifier`
- **Unique values**: 5
- **Non-null**: 3,444 (42.1%)
- **Top values**:

| Value | Count | % |
|-------|-------|---|
| nan | 4,729 | 57.9% |
| Bengaluru Central Corporation | 892 | 10.9% |
| Bengaluru West Corporation | 791 | 9.7% |
| Bengaluru North Corporation | 731 | 8.9% |
| Bengaluru South Corporation | 587 | 7.2% |
| Bengaluru East Corporation | 443 | 5.4% |

#### `map_file`
- **Unique values**: 0
- **Non-null**: 0 (0.0%)
- **Top values**:

| Value | Count | % |
|-------|-------|---|
| nan | 8,173 | 100.0% |

### 🔢 Numerical Features

#### `latitude`
- **Non-null**: 8,173 (100.0%)
- **Min**: 12.8010411
- **Max**: 13.2675104
- **Mean**: 12.987076
- **Std**: 0.060109
- **Median**: 12.9828467

#### `longitude`
- **Non-null**: 8,173 (100.0%)
- **Min**: 77.30873108
- **Max**: 77.76940255
- **Mean**: 77.596034
- **Std**: 0.061193
- **Median**: 77.58946

#### `endlatitude`
- **Non-null**: 8,004 (97.9%)
- **Min**: 0.0
- **Max**: 59.86013252
- **Mean**: 1.128050
- **Std**: 3.736845
- **Median**: 0.0
- **⚠️ Zero values**: 7,315 (likely placeholders)

#### `endlongitude`
- **Non-null**: 8,004 (97.9%)
- **Min**: 0.0
- **Max**: 80.72069138
- **Mean**: 6.678011
- **Std**: 21.761316
- **Median**: 0.0
- **⚠️ Zero values**: 7,315 (likely placeholders)

#### `resolved_at_latitude`
- **Non-null**: 74 (0.9%)
- **Min**: 12.8415683
- **Max**: 13.2572966
- **Mean**: 13.002599
- **Std**: 0.091377
- **Median**: 12.98371525

#### `resolved_at_longitude`
- **Non-null**: 74 (0.9%)
- **Min**: 77.3908201
- **Max**: 77.7126622
- **Mean**: 77.569049
- **Std**: 0.057246
- **Median**: 77.5561347

#### `age_of_truck`
- **Non-null**: 276 (3.4%)
- **Min**: 0.0
- **Max**: 2026.0
- **Mean**: 235.518116
- **Std**: 634.059816
- **Median**: 10.0

### 📅 Temporal Features

#### `start_datetime`
- **Non-null**: 8,057 (98.6%)
- **Min**: 2023-11-09 19:24:48.154000+00:00
- **Max**: 2024-04-08 17:11:42.780000+00:00
- **Range**: 150 days 21:46:54.626000

#### `end_datetime`
- **Non-null**: 475 (5.8%)
- **Min**: 2023-11-12 02:05:46+00:00
- **Max**: 2027-11-09 11:35:46+00:00
- **Range**: 1458 days 09:30:00

#### `modified_datetime`
- **Non-null**: 8,173 (100.0%)
- **Min**: 2023-11-09 20:35:47.789399+00:00
- **Max**: 2024-04-20 06:16:08.264418+00:00
- **Range**: 162 days 09:40:20.475019

#### `created_date`
- **Non-null**: 8,171 (100.0%)
- **Min**: 2023-09-29 23:38:19.342539+00:00
- **Max**: 2024-04-08 17:22:58.849385+00:00
- **Range**: 191 days 17:44:39.506846

#### `closed_datetime`
- **Non-null**: 3,141 (38.4%)
- **Min**: 2023-11-09 22:48:37.836256+00:00
- **Max**: 2024-04-20 06:16:08.118135+00:00
- **Range**: 162 days 07:27:30.281879

#### `resolved_datetime`
- **Non-null**: 74 (0.9%)
- **Min**: 2023-11-10 07:21:41.463359+00:00
- **Max**: 2024-04-02 22:33:50.469479+00:00
- **Range**: 144 days 15:12:09.006120

### 📝 Text Features

#### `address`
- **Non-null**: 8,170 (100.0%)
- **Avg length**: 94 chars
- **Max length**: 206 chars
- **Min length**: 24 chars
- **Unique values**: 3,089

#### `end_address`
- **Non-null**: 687 (8.4%)
- **Avg length**: 98 chars
- **Max length**: 199 chars
- **Min length**: 62 chars
- **Unique values**: 561

#### `description`
- **Non-null**: 6,813 (83.4%)
- **Avg length**: 52 chars
- **Max length**: 400 chars
- **Min length**: 1 chars
- **Unique values**: 5,542

#### `comment`
- **Non-null**: 0 (0.0%)

#### `resolved_at_address`
- **Non-null**: 74 (0.9%)
- **Avg length**: 96 chars
- **Max length**: 131 chars
- **Min length**: 66 chars
- **Unique values**: 58

#### `route_path`
- **Non-null**: 137 (1.7%)
- **Avg length**: 754 chars
- **Max length**: 7957 chars
- **Min length**: 1 chars
- **Unique values**: 83

#### `meta_data`
- **Non-null**: 0 (0.0%)

### 🔑 Identifier Features

#### `id`
- **Non-null**: 8,173 (100.0%)
- **Unique values**: 8,173

#### `veh_no`
- **Non-null**: 4,886 (59.8%)
- **Unique values**: 4,212

#### `client_id`
- **Non-null**: 8,173 (100.0%)
- **Unique values**: 2
- **Top values**:
  - `1`: 8093
  - `2`: 80

#### `created_by_id`
- **Non-null**: 8,171 (100.0%)
- **Unique values**: 1,898

#### `last_modified_by_id`
- **Non-null**: 8,170 (100.0%)
- **Unique values**: 304

#### `assigned_to_police_id`
- **Non-null**: 128 (1.6%)
- **Unique values**: 62

#### `citizen_accident_id`
- **Non-null**: 128 (1.6%)
- **Unique values**: 77

#### `closed_by_id`
- **Non-null**: 3,141 (38.4%)
- **Unique values**: 1,225

#### `resolved_by_id`
- **Non-null**: 74 (0.9%)
- **Unique values**: 42

#### `kgid`
- **Non-null**: 7,914 (96.8%)
- **Unique values**: 1,853
