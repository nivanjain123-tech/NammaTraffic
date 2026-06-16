# Demo Script — 5-Minute Judge Presentation

## Setup
- Laptop with browser open to the platform
- Map centered on Bengaluru
- 3 pre-loaded scenarios ready

---

## 0:00–0:30 — Problem Framing (30 sec)

> "Every day, Bengaluru sees 50+ traffic incidents — breakdowns, accidents, tree falls, protests. Right now, every incident is handled reactively. No predictions. No learning from the past. No data-backed resource allocation.
> 
> We built the **Bengaluru Traffic Incident Intelligence Platform** — a system that predicts, recommends, and learns. Let me show you."

*[Show: Live map with historical incident dots across Bengaluru]*

---

## 0:30–1:30 — Live Incident Flow (60 sec)

> "A new incident just came in — a heavy vehicle breakdown on the Outer Ring Road near Marathahalli at 5:47 PM."

**Action:** Click "New Incident" → Fill: vehicle_breakdown, ORR, lat/lon

*[The system instantly responds with:]*

> "Watch what happens. The system automatically predicts:
> - **Severity:** HIGH (87% confidence)
> - **Road Closure:** Unlikely (4.3%)  
> - **Estimated Resolution:** 42 minutes
> - **Resources needed:** 2 officers, 1 tow truck
> 
> All of this — in under 200 milliseconds. No phone calls. No guesswork."

*[Show: Enriched incident card with severity badge, timeline, resource recommendation]*

---

## 1:30–2:30 — Similar Incident Search (60 sec)

> "But here's where it gets powerful. The system found 5 similar incidents from the past."

*[Show: Similar incidents panel]*

> "FKID001234 — a breakdown at the same junction in February. Resolved in 38 minutes with 2 officers. The resolution notes say they diverted traffic via Kundalahalli Gate.
>
> This is **institutional memory**. Every incident the department has ever handled becomes a playbook for the next one."

---

## 2:30–3:30 — Risk Map & Hotspots (60 sec)

> "Let's zoom out. This heatmap shows incident density across Bengaluru."

*[Toggle heatmap layer on]*

> "The red zones — Silk Board, Marathahalli, Hebbal — these are chronic hotspots. But watch this..."

*[Toggle time slider to show morning vs evening]*

> "The risk landscape shifts completely between morning and evening peak. Our system knows this and adjusts predictions in real-time.
>
> Traffic commanders can use this to **pre-position** resources at high-risk locations before incidents even happen."

---

## 3:30–4:30 — AI Copilot (60 sec)

> "Now, the feature that changes everything — our AI Traffic Copilot."

*[Open chat panel]*

**Type:** "What is the expected impact of a protest on Bellary Road at 4 PM?"

*[System responds:]*

> "Based on 15 historical protests on Bellary Road:
> - Road closure probability: 40%
> - Expected duration: 3-4 hours
> - Recommended: 5 officers, 6 barricades
> - Suggested diversion: Sankey Road → Palace Road
>
> The copilot doesn't guess — it queries our entire historical database and gives operators data-backed answers in natural language. No SQL. No dashboards. Just ask."

---

## 4:30–5:00 — Impact Statement (30 sec)

> "Bengaluru Traffic Police handles 15,000+ incidents per year with no predictive tools, no institutional memory, and no data-backed resource planning.
>
> Our platform:
> - **Predicts** severity and resolution time for every incident
> - **Recommends** exact resources needed
> - **Learns** from every closed incident
> - **Speaks** natural language through the AI copilot
>
> This isn't a dashboard. This is a **command platform** that makes Bengaluru's traffic operations proactive instead of reactive.
>
> Thank you."

---

## Backup Scenarios (if judges ask)

1. **"What about planned events?"** → Show a VIP movement scenario with pre-planned road closure and diversion
2. **"How accurate are the predictions?"** → Show CV results: F1 ~85% severity, PR-AUC ~80% closure
3. **"Can this scale?"** → Show Docker deployment architecture, <200ms inference
4. **"What data do you need?"** → "Just the incident data your Astram system already collects"
