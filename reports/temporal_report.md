# ⏰ Temporal Report

## Date Range

- **start_datetime**: 2023-11-09 19:24:48.154000+00:00 → 2024-04-08 17:11:42.780000+00:00 (8,057 non-null)
- **end_datetime**: 2023-11-12 02:05:46+00:00 → 2027-11-09 11:35:46+00:00 (475 non-null)
- **modified_datetime**: 2023-11-09 20:35:47.789399+00:00 → 2024-04-20 06:16:08.264418+00:00 (8,173 non-null)
- **created_date**: 2023-09-29 23:38:19.342539+00:00 → 2024-04-08 17:22:58.849385+00:00 (8,171 non-null)
- **closed_datetime**: 2023-11-09 22:48:37.836256+00:00 → 2024-04-20 06:16:08.118135+00:00 (3,141 non-null)
- **resolved_datetime**: 2023-11-10 07:21:41.463359+00:00 → 2024-04-02 22:33:50.469479+00:00 (74 non-null)

**Primary time range**: 2023-11-09 19:24:48.154000+00:00 to 2024-04-08 17:11:42.780000+00:00
**Duration span**: 150 days

## Monthly Distribution (start_datetime)

| Month | Count | % |
|-------|-------|---|
| 2023-11 | 972 | 11.9% |
| 2023-12 | 1,746 | 21.4% |
| 2024-01 | 1,446 | 17.7% |
| 2024-02 | 1,340 | 16.4% |
| 2024-03 | 1,931 | 23.6% |
| 2024-04 | 622 | 7.6% |

## Day of Week Distribution

| Day | Count | % |
|-----|-------|---|
| Monday | 909 | 11.1% |
| Tuesday | 1,245 | 15.2% |
| Wednesday | 1,162 | 14.2% |
| Thursday | 1,343 | 16.4% |
| Friday | 1,245 | 15.2% |
| Saturday | 1,223 | 15.0% |
| Sunday | 930 | 11.4% |

## Hourly Distribution (24h)

| Hour | Count | % | Bar |
|------|-------|---|-----|
| 00:00 | 418 | 5.1% | ███████████████ |
| 01:00 | 381 | 4.7% | ██████████████ |
| 02:00 | 387 | 4.7% | ██████████████ |
| 03:00 | 372 | 4.6% | █████████████ |
| 04:00 | 558 | 6.8% | ████████████████████ |
| 05:00 | 661 | 8.1% | ████████████████████████ |
| 06:00 | 660 | 8.1% | ████████████████████████ |
| 07:00 | 480 | 5.9% | █████████████████ |
| 08:00 | 327 | 4.0% | ████████████ |
| 09:00 | 160 | 2.0% | █████ |
| 10:00 | 68 | 0.8% | ██ |
| 11:00 | 68 | 0.8% | ██ |
| 12:00 | 63 | 0.8% | ██ |
| 13:00 | 33 | 0.4% | █ |
| 14:00 | 13 | 0.2% |  |
| 15:00 | 9 | 0.1% |  |
| 16:00 | 9 | 0.1% |  |
| 17:00 | 34 | 0.4% | █ |
| 18:00 | 228 | 2.8% | ████████ |
| 19:00 | 578 | 7.1% | █████████████████████ |
| 20:00 | 681 | 8.3% | █████████████████████████ |
| 21:00 | 810 | 9.9% | ██████████████████████████████ |
| 22:00 | 564 | 6.9% | ████████████████████ |
| 23:00 | 495 | 6.1% | ██████████████████ |

### Peak Hours Analysis

**Top 3 busiest hours**:
- 21:00 → 810 events
- 20:00 → 681 events
- 05:00 → 661 events

**Bottom 3 quietest hours**:
- 15:00 → 9 events
- 16:00 → 9 events
- 14:00 → 13 events

## Time-to-Resolve Analysis

- **Records with resolution time**: 3,195
- **Records with positive resolution time**: 3,192
- **Mean resolution time**: 103.8 hours
- **Median resolution time**: 1.1 hours
- **Std resolution time**: 339.1 hours
- **Min resolution time**: 0.01 hours
- **Max resolution time**: 3363.2 hours
- **25th percentile**: 0.47 hours
- **75th percentile**: 5.44 hours
- **90th percentile**: 278.47 hours
- **95th percentile**: 639.86 hours

- **⚠️ Negative resolution times**: 3 (data quality issue)

### Resolution Time by Event Cause

| Event Cause | Count | Mean (hrs) | Median (hrs) |
|-------------|-------|-----------|-------------|
| vehicle_breakdown | 1,836 | 0.8 | 0.7 |
| others | 419 | 206.5 | 7.1 |
| water_logging | 244 | 204.1 | 59.7 |
| pot_holes | 175 | 586.4 | 216.4 |
| tree_fall | 174 | 101.8 | 12.2 |
| construction | 118 | 227.7 | 49.1 |
| road_conditions | 92 | 431.5 | 153.9 |
| accident | 91 | 0.8 | 0.7 |
| congestion | 22 | 1.2 | 1.2 |
| procession | 13 | 0.9 | 0.6 |
| Debris | 4 | 1621.7 | 1447.6 |
| protest | 2 | 0.4 | 0.4 |
| test_demo | 2 | 0.0 | 0.0 |

### Resolution Time by Priority

| Priority | Count | Mean (hrs) | Median (hrs) |
|----------|-------|-----------|-------------|
| High | 1,967 | 86.0 | 1.0 |
| Low | 1,225 | 132.5 | 1.2 |

## Created vs Start DateTime Gap

- **Records with both**: 8,057
- **Mean gap**: 3.7 minutes
- **Median gap**: 1.5 minutes
- **Negative gaps (created before start)**: 45

## Event Type by Time of Day

| Event Type | Night | Morning | Afternoon | Evening |
|---|---|---|---|---|
| planned | 102 | 45 | 12 | 206 |
| unplanned | 2675 | 1718 | 149 | 3150 |