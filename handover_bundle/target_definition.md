# 🎯 Target Definition Report

## What Can We Predict?

Analysis of potential prediction targets for the hackathon.

---
### Target 1: Road Closure Prediction (`requires_road_closure`)

**Distribution**:

| Value | Count | % |
|-------|-------|---|
| False | 7,497 | 91.7% |
| True | 676 | 8.3% |

**Feasibility**: ⚠️ Highly imbalanced
**Type**: Binary Classification
**Usable features**: event_cause, corridor, priority, hour, day_of_week, zone, description

---
### Target 2: Event Type Classification (`event_type`)

**Distribution**:

| Value | Count | % |
|-------|-------|---|
| unplanned | 7,706 | 94.3% |
| planned | 467 | 5.7% |

**Feasibility**: ✅ Reasonable
**Type**: Multi-class Classification

---
### Target 3: Priority Prediction (`priority`)

**Distribution**:

| Value | Count | % |
|-------|-------|---|
| High | 5,030 | 61.5% |
| Low | 3,141 | 38.4% |
| nan | 2 | 0.0% |

**Type**: Ordinal Classification

---
### Target 4: Resolution Time Prediction

- **Usable records**: 3,192 (39.1%)
- **Mean**: 103.8 hours
- **Median**: 1.1 hours
- **Skewness**: 4.97

**Binned distribution (for classification approach)**:

| Bin | Count | % |
|-----|-------|---|
| <30min | 849 | 26.6% |
| 30min-1h | 653 | 20.5% |
| 1-2h | 678 | 21.2% |
| 2-4h | 186 | 5.8% |
| 4-12h | 82 | 2.6% |
| 12-24h | 76 | 2.4% |
| >24h | 668 | 20.9% |

**Type**: Regression or Binned Classification
**Usable features**: event_cause, event_type, corridor, priority, hour, day_of_week, zone, veh_type

---
### Target 5: Event Cause Prediction (`event_cause`)

**Distribution**:

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
| Fog / Low Visibility | 2 | 0.0% |
| debris | 1 | 0.0% |

**Type**: Multi-class Classification

---
### Target 6: Spatial-Temporal Hotspot Prediction

**Concept**: Predict where and when the next incident will occur

**Approach**: Grid the city into spatial bins, predict incident count per bin per time window

**Features**: Historical patterns, corridor, zone, junction, time features

**Type**: Regression (count prediction) or Classification (high/low risk)


---
## Feature Correlation with Targets

### Road Closure by Event Cause


| Event Cause | FALSE % | TRUE % |
|-------------|---------|--------|
| Debris | 91.7% | 8.3% |
| Fog / Low Visibility | 100.0% | 0.0% |
| accident | 97.0% | 3.0% |
| congestion | 95.6% | 4.4% |
| construction | 73.5% | 26.5% |
| debris | 0.0% | 100.0% |
| others | 91.4% | 8.6% |
| pot_holes | 97.6% | 2.4% |
| procession | 73.6% | 26.4% |
| protest | 60.0% | 40.0% |
| public_event | 53.6% | 46.4% |
| road_conditions | 87.6% | 12.4% |
| test_demo | 100.0% | 0.0% |
| tree_fall | 60.6% | 39.4% |
| vehicle_breakdown | 95.7% | 4.3% |
| vip_movement | 20.0% | 80.0% |
| water_logging | 91.5% | 8.5% |

### Road Closure by Priority


| Priority | FALSE % | TRUE % |
|----------|---------|--------|
| High | 94.1% | 5.9% |
| Low | 87.9% | 12.1% |

---
## 🏆 Recommended Targets for Hackathon


| Rank | Target | Type | Records | Why |
|------|--------|------|---------|-----|
| 1 | **Resolution Time** | Regression | 3,192 | High business impact, good feature set |
| 2 | **Road Closure** | Binary Classification | 8,173 | Clear binary target, actionable |
| 3 | **Priority** | Ordinal Classification | 8,171 | Good for triage automation |
| 4 | **Event Cause** | Multi-class | 8,173 | Useful for dispatching |
| 5 | **Hotspot Prediction** | Spatial-Temporal | 8,173 | Proactive traffic management |
