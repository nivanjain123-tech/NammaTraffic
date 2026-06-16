# AI Traffic Copilot Design — Phase 9

## Vision

A natural language interface that lets traffic operators ask questions about incidents, get predictions, find patterns, and receive recommendations — without needing SQL, dashboards, or analytics training.

---

## Architecture

```
User Question
    ↓
┌──────────────────────────────────────┐
│         Intent Classifier            │
│  (keyword + pattern matching)        │
│                                      │
│  Categories:                         │
│  - incident_query                    │
│  - prediction_request                │
│  - similar_search                    │
│  - trend_analysis                    │
│  - recommendation                    │
│  - general_info                      │
└──────────┬───────────────────────────┘
           ↓
┌──────────────────────────────────────┐
│      Context Builder (RAG)           │
│                                      │
│  1. Query incident database          │
│  2. Retrieve relevant statistics     │
│  3. Fetch similar incidents          │
│  4. Get current predictions          │
│  5. Assemble context document        │
└──────────┬───────────────────────────┘
           ↓
┌──────────────────────────────────────┐
│      LLM Generation (Gemini)         │
│                                      │
│  System Prompt + Context + Question  │
│  → Structured Response               │
└──────────┬───────────────────────────┘
           ↓
┌──────────────────────────────────────┐
│      Response Formatter              │
│                                      │
│  - Structured cards                  │
│  - Inline data tables                │
│  - Map coordinates                   │
│  - Action buttons                    │
└──────────────────────────────────────┘
```

---

## Retrieval Strategy

### Data Sources for Context

| Source | What it provides | When used |
|---|---|---|
| Incident DB | Historical incidents matching query filters | Always |
| Prediction API | ML predictions for specific scenarios | prediction_request |
| Analytics API | Aggregated statistics, trends | trend_analysis |
| Similar Search | Top-K similar incidents | similar_search |
| Corridor Risk | Current risk scores per corridor | recommendation |

### Retrieval Pipeline
```python
async def build_context(question: str, intent: str) -> str:
    context_parts = []
    
    # Always: relevant incident statistics
    stats = await get_incident_stats(extract_filters(question))
    context_parts.append(f"Dataset Statistics:\n{stats}")
    
    if intent == 'prediction_request':
        params = extract_scenario(question)
        prediction = await get_prediction(params)
        context_parts.append(f"ML Predictions:\n{prediction}")
    
    if intent == 'similar_search':
        similar = await find_similar_incidents(question)
        context_parts.append(f"Similar Incidents:\n{similar}")
    
    if intent in ['recommendation', 'trend_analysis']:
        analytics = await get_analytics(extract_filters(question))
        context_parts.append(f"Analytics:\n{analytics}")
    
    return "\n\n---\n\n".join(context_parts)
```

---

## System Prompt

```
You are the Bengaluru Traffic Intelligence Copilot, an AI assistant for traffic 
police operations in Bengaluru, India.

You have access to a database of {total_incidents} historical traffic incidents 
from November 2023 to April 2024, covering {n_corridors} corridors across 
{n_zones} zones.

Your capabilities:
1. Answer questions about historical incident patterns
2. Provide predictions for new incident scenarios
3. Find similar past incidents and their resolutions
4. Recommend resources (officers, barricades, tow trucks)
5. Suggest diversion routes when road closures are likely
6. Explain trends and anomalies in traffic data

Rules:
- Always cite specific numbers from the data
- When giving predictions, state confidence levels
- If you don't have enough data to answer, say so explicitly
- Format responses with clear sections and bullet points
- Include actionable recommendations when relevant
- Reference specific incident IDs when discussing examples
- Never fabricate data or statistics
```

---

## Example Interactions

### Q1: Prediction Query
**User:** "What is the expected impact of a breakdown at Silk Board Junction at 6 PM?"

**Context Retrieved:**
- 312 vehicle breakdowns near Silk Board (within 2km)
- 89 occurred during 5-8 PM peak
- Road closure rate: 3.2% for breakdowns
- Median resolution: 42 minutes
- Priority distribution: 78% High, 22% Low

**Response:**
> Based on 89 historical vehicle breakdowns near Silk Board Junction during evening peak hours:
> 
> **Severity:** High (78% probability)
> **Road Closure:** Unlikely (3.2%)
> **Resolution Time:** ~42 minutes (median)
> **Recommended Resources:** 2 officers + 1 tow truck
> 
> ⚠️ Silk Board Junction is a critical interchange — even without road closure, expect significant queuing on ORR approaches.
> 
> **Most similar incident:** FKID001234 (Feb 15, 2024) — heavy vehicle breakdown, resolved in 38 minutes with 2 officers.

### Q2: Trend Analysis
**User:** "Which corridors had the most incidents last month?"

### Q3: Recommendation
**User:** "We have a VIP movement on Bellary Road tomorrow at 10 AM. What should we prepare?"

### Q4: Similar Search
**User:** "Show me past tree falls during monsoon season on Ring Road"

---

## Guardrails

| Guardrail | Implementation |
|---|---|
| **No hallucination** | All statistics must come from retrieved context, not generated |
| **Out-of-scope detection** | If question is about non-traffic topics, politely redirect |
| **Confidence bounds** | Always state "based on N incidents" to convey statistical reliability |
| **No PII exposure** | Never return vehicle numbers, citizen IDs, or officer names |
| **Latency cap** | Total response time < 5 seconds (retrieval + generation) |
| **Token limit** | Max 500 tokens per response to keep answers concise |

---

## Output Format

Every copilot response includes:

```json
{
  "text": "Structured markdown response",
  "sources": ["FKID001234", "FKID002345"],
  "confidence": 0.85,
  "actions": [
    { "label": "Show on map", "type": "map_navigate", "params": {} },
    { "label": "Deploy resources", "type": "dispatch", "params": {} },
    { "label": "View similar incidents", "type": "search", "params": {} }
  ],
  "visualizations": [
    { "type": "bar_chart", "data": {...}, "title": "Incidents by Hour" }
  ]
}
```
