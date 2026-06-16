# 🔍 Data Quality Report

## 1. Duplicate Analysis

- **Duplicate IDs**: 0
- **Unique IDs**: 8,173
- **Total rows**: 8,173

## 2. Coordinate Anomalies

- **latitude == 0**: 0
- **longitude == 0**: 0
- **latitude outside Bengaluru (12-14)**: 0
- **longitude outside Bengaluru (76-78.5)**: 0
- **endlatitude == 0**: 7315
- **endlongitude == 0**: 7315

> ⚠️ 7315 records have (0,0) end coordinates — likely unused/not applicable

## 3. Temporal Anomalies

- **Future start_datetime**: 0
- **end_datetime before start_datetime**: 48
- **Negative resolution times**: 3
- **Resolution > 30 days**: 143
- **Resolution > 90 days**: 22

## 4. Status Consistency

**Status distribution**:

- `closed`: 7,095
- `active`: 1,007
- `resolved`: 71

- **Status='closed' but no closed_datetime**: 3956
- **Status='resolved' but no resolved_datetime**: 2
- **Status='open' but has resolved_datetime**: 0

## 5. Text Field Quality

- **Descriptions available**: 6,813
- **Very short (<5 chars)**: 155
- **Very long (>500 chars)**: 0
- **Contains Kannada text**: 870

## 6. Low-Variance Columns

- **`client_id`**: near-constant, dominant value `1` = 99.0%

## 7. Anonymized Fields Analysis

- **`id`**: 8,173 non-null, 8,173 unique
- **`veh_no`**: 4,886 non-null, 4,212 unique
- **`created_by_id`**: 8,171 non-null, 1,898 unique
- **`last_modified_by_id`**: 8,170 non-null, 304 unique
- **`assigned_to_police_id`**: 128 non-null, 62 unique
- **`citizen_accident_id`**: 128 non-null, 77 unique
- **`closed_by_id`**: 3,141 non-null, 1,225 unique
- **`resolved_by_id`**: 74 non-null, 42 unique
- **`kgid`**: 7,914 non-null, 1,853 unique
- **`gba_identifier`**: 3,444 non-null, 5 unique

## 8. Vehicle Data Quality

- **veh_type populated**: 4,887 (59.8%)
- **Unique vehicle types**: 10
  - `bmtc_bus`: 1,466
  - `heavy_vehicle`: 965
  - `lcv`: 678
  - `others`: 449
  - `private_bus`: 359
  - `private_car`: 345
  - `truck`: 276
  - `ksrtc_bus`: 217
  - `taxi`: 95
  - `auto`: 37
- **veh_no populated**: 4,886 (59.8%)

### Breakdown-specific fields (should correlate with event_cause=vehicle_breakdown)

- **`cargo_material`**: 276 in breakdowns, 0 in non-breakdowns
- **`reason_breakdown`**: 276 in breakdowns, 0 in non-breakdowns
- **`age_of_truck`**: 276 in breakdowns, 0 in non-breakdowns

## 9. Boolean Field Encoding

- **`requires_road_closure`** unique values: [False, True]
- dtype: bool
- **`authenticated`** unique values: ['yes', 'no']

## 10. Complex Fields

- **`route_path`**: 137 non-null (1.7%)
  - Sample: `[]`
- **`meta_data`**: 0 non-null (0.0%)

---
## 📋 Recommendations


### Data Cleaning
1. **Replace (0,0) end coordinates with NaN** — 7,315 records have placeholder zeros
2. **Convert 'NULL' strings to proper NaN** — Done during loading
3. **Parse datetime columns consistently** — Ensure timezone handling is uniform
4. **Handle Kannada text** in descriptions — Consider translation or transliteration for NLP features
5. **Remove constant columns** — `client_id` appears constant

### Feature Engineering
1. **Time features**: hour, day_of_week, month, is_weekend, is_rush_hour (8-10, 17-19)
2. **Resolution time**: target variable (use log transform due to skewness)
3. **Spatial features**: distance from city center, cluster ID from lat/lon
4. **Text features**: description length, language detection, keyword extraction
5. **Corridor encoding**: one-hot or target encoding for corridors
6. **Historical features**: events per corridor in last N hours

### Modeling Considerations
1. **Class imbalance**: road_closure is imbalanced — use SMOTE or class weights
2. **Missing data strategy**: Different columns have different missingness patterns
3. **Temporal split**: Use time-based train/test split, not random
4. **Feature leakage**: Don't use resolved_datetime, closed_datetime, resolved_at_* as input features
