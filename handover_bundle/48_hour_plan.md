# 48-Hour Build Plan

## MUST HAVE (Hours 0–24)
*Everything in the 24-hour plan, plus:*

These are non-negotiable for a competitive submission.

| # | Feature | Hours | Priority |
|---|---|---|---|
| 1 | Database + data loading | 2h | 🔴 Critical |
| 2 | ML pipeline (3 models trained) | 4h | 🔴 Critical |
| 3 | Backend API (predictions, search, analytics) | 4h | 🔴 Critical |
| 4 | Map UI with incident markers + heatmap | 4h | 🔴 Critical |
| 5 | Incident detail panel with predictions | 2h | 🔴 Critical |
| 6 | AI Copilot (basic Q&A) | 4h | 🔴 Critical |
| 7 | Cloud deployment | 2h | 🔴 Critical |
| 8 | Demo rehearsal | 2h | 🔴 Critical |

---

## SHOULD HAVE (Hours 24–36)
*Features that significantly boost judge impression.*

| # | Feature | Hours | Priority |
|---|---|---|---|
| 9 | Resource Allocation Recommender UI | 2h | 🟡 High |
| 10 | Diversion route visualization on map | 3h | 🟡 High |
| 11 | Corridor risk dashboard with charts | 2h | 🟡 High |
| 12 | Time slider for historical playback | 2h | 🟡 High |
| 13 | H3 hexagonal risk grid on map | 2h | 🟡 High |
| 14 | Copilot response cards with actions | 1h | 🟡 High |

---

## NICE TO HAVE (Hours 36–48)
*Polish and differentiators.*

| # | Feature | Hours | Priority |
|---|---|---|---|
| 15 | Post-Event Learning dashboard (KPIs, trends) | 2h | 🟢 Medium |
| 16 | Dark mode command center theme | 1h | 🟢 Medium |
| 17 | WebSocket real-time incident simulation | 2h | 🟢 Medium |
| 18 | PDF report export | 1h | 🟢 Medium |
| 19 | Mobile-responsive layout | 1h | 🟢 Medium |
| 20 | Performance benchmarks in presentation slides | 1h | 🟢 Medium |
| 21 | Video recording of demo as backup | 1h | 🟢 Medium |
| 22 | Architecture diagrams for slides | 1h | 🟢 Medium |
| 23 | Final polish, edge cases, error handling | 2h | 🟢 Medium |

---

## Hour-by-Hour Schedule

### Day 1

| Time | Task |
|---|---|
| 00:00–02:00 | Project setup, DB, data loading |
| 02:00–06:00 | ML pipeline: feature eng + 3 models |
| 06:00–10:00 | Backend API: CRUD + predictions + search |
| 10:00–14:00 | Frontend: Map + markers + heatmap |
| 14:00–16:00 | Incident panel + new incident flow |
| 16:00–20:00 | AI Copilot integration |
| 20:00–24:00 | Deploy + smoke test + demo prep |

### Day 2

| Time | Task |
|---|---|
| 24:00–26:00 | Resource recommender UI |
| 26:00–29:00 | Diversion routes + corridor dashboard |
| 29:00–31:00 | Time slider + H3 grid |
| 31:00–32:00 | Copilot polish |
| 32:00–34:00 | Post-event learning dashboard |
| 34:00–36:00 | Dark mode + responsive fixes |
| 36:00–38:00 | WebSocket simulation |
| 38:00–42:00 | Final polish + edge cases |
| 42:00–44:00 | Architecture slides + benchmarks |
| 44:00–46:00 | Full demo rehearsal (3 runs) |
| 46:00–48:00 | Record backup video + final deploy |

---

## Risk Mitigation

| Risk | Mitigation |
|---|---|
| ML model performance is poor | Use simpler rule-based fallbacks; show model improvement path |
| Deployment fails | Have Docker Compose local demo ready |
| Gemini API rate limit | Cache common copilot responses; pre-generate top 10 scenarios |
| Map performance with 8K points | Use marker clustering; show heatmap by default |
| Time overrun on frontend | Prioritize map + incident panel; skip polish features |
