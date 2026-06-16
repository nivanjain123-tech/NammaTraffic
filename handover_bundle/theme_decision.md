# Theme Decision Log

## Selected Theme
**Event-Driven Congestion (Planned & Unplanned)**

## Decision Date
2026-06-16

## Scoring Summary

| Theme | Score |
|---|---|
| Parking-Induced Congestion | 5.30/10 |
| **Event-Driven Congestion** | **8.90/10** |
| Computer Vision | 4.15/10 |

## Evidence-Based Justification

### Why Event-Driven Congestion Won

1. **Data completeness**: The Astram dataset provides a complete incident lifecycle with 45 columns across geospatial, temporal, causal, and organizational dimensions. Every major ML task (classification, regression, similarity search) is supported.

2. **Multiple prediction targets**: Priority, road closure, resolution time, event cause, and resource needs are all directly derivable — giving us 5 distinct ML models to showcase.

3. **Product depth**: The theme naturally supports a full command platform with 8 integrated modules. This is a PRODUCT story, not a dashboard story.

4. **AI Copilot opportunity**: The richness of the incident data makes RAG-based copilot Q&A genuinely useful — operators can ask "What happened last time there was a tree fall on Outer Ring Road at 6 PM?" and get a real, data-backed answer.

5. **Operational credibility**: The dataset literally comes from Bengaluru Traffic Police's Astram system. We're building on their actual workflow.

6. **Demo impact**: A 5-minute demo can show: live map → incoming incident → AI predicts severity → recommends resources → suggests diversion → copilot answers follow-up question. That's a complete story arc.

### Why Parking-Induced Congestion Was Rejected

- The violation dataset (298K rows) contains only parking violation records with location and vehicle info.
- The problem statement asks to "quantify impact on traffic flow" — but there is **no traffic flow data** in the dataset.
- Building a heatmap of violations is trivial and many teams will do exactly this.
- The product ceiling is low: essentially a heatmap dashboard with enforcement zone prioritization.

### Why Computer Vision Was Rejected

- **No image dataset was provided.** The theme requires processing traffic images, detecting vehicles, classifying violations — all impossible without labeled training images.
- Building object detection + violation classification + license plate recognition in 48 hours without data is infeasible.
- The submission would be a conceptual mockup, not a working prototype.
- Even with synthetic data, the model would not demonstrate real competence.
