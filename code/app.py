"""
NammaTraffic — Streamlit Command Center App
Bengaluru Traffic Incident Intelligence & Command Platform
Flipkart Gridlock Hackathon 2.0

Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import pickle
import urllib.request
import urllib.error

import plotly.express as px
import plotly.graph_objects as go

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="NammaTraffic — Bengaluru Traffic Intelligence",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ===================== CUSTOM CSS =====================
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }

    .metric-card {
        background: linear-gradient(135deg, #1a1f2e 0%, #252b3b 100%);
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 20px;
        margin: 8px 0;
        text-align: center;
    }
    .metric-value {
        font-size: 2.2em;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-label {
        font-size: 0.85em;
        color: #a0aec0;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 4px;
    }

    .severity-high {
        background: linear-gradient(135deg, #fc5c65 0%, #eb3b5a 100%);
        color: white; padding: 4px 12px; border-radius: 20px;
        font-weight: 700; display: inline-block;
    }
    .severity-low {
        background: linear-gradient(135deg, #45aaf2 0%, #2d98da 100%);
        color: white; padding: 4px 12px; border-radius: 20px;
        font-weight: 700; display: inline-block;
    }

    .incident-card {
        background: #1a1f2e;
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        border-left: 4px solid #667eea;
    }

    .risk-high { color: #fc5c65; font-weight: 700; }
    .risk-medium { color: #f7b731; font-weight: 700; }
    .risk-low { color: #26de81; font-weight: 700; }

    .live-feed {
        background: #1a1f2e;
        border: 1px solid #fc5c65;
        border-radius: 8px;
        padding: 10px 16px;
        overflow: hidden;
        white-space: nowrap;
    }
    .live-feed-inner {
        display: inline-block;
        animation: scroll-left 40s linear infinite;
    }
    @keyframes scroll-left {
        0% { transform: translateX(0); }
        100% { transform: translateX(-50%); }
    }

    .explain-bar {
        background: #252b3b;
        border-radius: 6px;
        padding: 8px 12px;
        margin: 4px 0;
        border-left: 3px solid #667eea;
    }

    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0e1117 0%, #1a1f2e 100%);
    }

    .header-gradient {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2em;
        font-weight: 800;
    }
</style>
""", unsafe_allow_html=True)

# ===================== PATHS & DATA =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS_DIR = os.path.join(BASE_DIR, "..", "artifacts")

DOW_MAP = {
    "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
    "Friday": 4, "Saturday": 5, "Sunday": 6,
}

DEMO_SCENARIOS = {
    "🚨 Scenario 1: Severe Accident — Silk Board (6 PM)": {
        "cause": "accident", "event_type": "unplanned", "corridor": "Hosur Road",
        "hour": 18, "dow": "Friday", "veh": "heavy_vehicle",
    },
    "🌳 Scenario 2: Tree Fall — Bellary Road (Morning Rush)": {
        "cause": "tree_fall", "event_type": "unplanned", "corridor": "Bellary Road 1",
        "hour": 8, "dow": "Monday", "veh": "unknown",
    },
    "✊ Scenario 3: VIP Movement — ORR North (Peak Hour)": {
        "cause": "vip_movement", "event_type": "planned", "corridor": "ORR North 1",
        "hour": 17, "dow": "Wednesday", "veh": "unknown",
    },
}

CAUSE_LABELS = {
    "accident": "Accident", "vehicle_breakdown": "Vehicle Breakdown",
    "tree_fall": "Tree Fall", "vip_movement": "VIP Movement",
    "protest": "Protest", "construction": "Construction",
    "public_event": "Public Event", "procession": "Procession",
}


@st.cache_data
def load_data():
    df = pd.read_csv(os.path.join(ARTIFACTS_DIR, "cleaned_data.csv"))
    df["start_datetime"] = pd.to_datetime(df["start_datetime"], errors="coerce", utc=True)
    return df


@st.cache_data
def load_corridor_risk():
    return pd.read_csv(os.path.join(ARTIFACTS_DIR, "corridor_risk.csv"))


@st.cache_data
def load_hotspot_clusters():
    return pd.read_csv(os.path.join(ARTIFACTS_DIR, "hotspot_clusters.csv"))


@st.cache_data
def load_model_performance():
    with open(os.path.join(ARTIFACTS_DIR, "model_performance.json"), "r") as f:
        return json.load(f)


@st.cache_data
def load_similarity_features():
    path = os.path.join(ARTIFACTS_DIR, "similarity_features.npy")
    try:
        return np.load(path)
    except ValueError:
        # Legacy artifact saved with mixed bool/float columns (object dtype)
        return np.load(path, allow_pickle=True).astype(np.float64)


@st.cache_data
def load_copilot_context():
    with open(os.path.join(ARTIFACTS_DIR, "copilot_context.json"), "r") as f:
        return json.load(f)


@st.cache_resource
def load_ml_models():
    from catboost import CatBoostClassifier, CatBoostRegressor
    import lightgbm as lgb

    severity = CatBoostClassifier()
    severity.load_model(os.path.join(ARTIFACTS_DIR, "severity_model.cbm"))
    resolution = CatBoostRegressor()
    resolution.load_model(os.path.join(ARTIFACTS_DIR, "resolution_model.cbm"))
    closure = lgb.Booster(model_file=os.path.join(ARTIFACTS_DIR, "closure_model.lgb"))
    with open(os.path.join(ARTIFACTS_DIR, "label_encoders.pkl"), "rb") as f:
        le_dict = pickle.load(f)
    with open(os.path.join(ARTIFACTS_DIR, "feature_config.json"), "r") as f:
        feature_config = json.load(f)
    return severity, closure, resolution, le_dict, feature_config


try:
    df = load_data()
    corridor_risk = load_corridor_risk()
    hotspot_clusters = load_hotspot_clusters()
    model_perf = load_model_performance()
    sim_features = load_similarity_features()
    copilot_ctx = load_copilot_context()
    DATA_LOADED = True
except Exception as e:
    DATA_LOADED = False
    st.error(f"⚠️ Run `python train_pipeline.py` first to generate artifacts. Error: {e}")


# ===================== HELPERS =====================
def find_similar_incidents(idx, top_k=5):
    from sklearn.metrics.pairwise import cosine_similarity
    query = sim_features[idx].reshape(1, -1)
    sims = cosine_similarity(query, sim_features)[0]
    sims[idx] = -1
    top_indices = np.argsort(sims)[-top_k:][::-1]
    return top_indices, sims[top_indices]


def estimate_resources(cause, priority, closure_prob):
    resources = {"officers": 1, "barricades": 0, "tow_truck": False, "ambulance": False}
    if priority == "High":
        resources["officers"] = 3
    if closure_prob > 0.3:
        resources["barricades"] = 4
        resources["officers"] += 2
    if cause == "vehicle_breakdown":
        resources["tow_truck"] = True
    elif cause == "accident":
        resources["officers"] += 2
        resources["ambulance"] = True
        resources["barricades"] = 2
    elif cause in ["protest", "public_event", "vip_movement", "procession"]:
        resources["officers"] += 4
        resources["barricades"] = 8
    elif cause == "tree_fall":
        resources["officers"] += 1
        resources["barricades"] = 2
    elif cause == "construction":
        resources["barricades"] = 6
    return resources


def build_feature_row(cause, event_type, corridor, hour, dow, veh_type):
    """Build ML feature row matching train_pipeline.py logic."""
    cause_counts = df["event_cause"].value_counts()
    cause_grouped = cause if cause_counts.get(cause, 0) >= 50 else "other_rare"
    corridor_counts = df["corridor"].value_counts()
    corridor_grouped = corridor if corridor_counts.get(corridor, 0) >= 30 else "Other_Corridor"
    veh_counts = df["veh_type_clean"].value_counts()
    veh_clean = veh_type if veh_counts.get(veh_type, 0) >= 20 else "other_vehicle"

    corr_row = corridor_risk[corridor_risk["corridor"] == corridor]
    if len(corr_row):
        lat, lon = corr_row.iloc[0]["lat"], corr_row.iloc[0]["lon"]
        corr_incidents = corr_row.iloc[0]["total_incidents"]
        corr_closure = corr_row.iloc[0]["closure_rate"]
        corr_priority = corr_row.iloc[0]["high_priority_pct"]
    else:
        lat, lon = 12.9716, 77.5946
        corr_incidents, corr_closure, corr_priority = 100, 0.05, 0.5

    lat_bin = round(lat, 3)
    lon_bin = round(lon, 3)
    geo_bin = f"{lat_bin}_{lon_bin}"
    geo_density = (df["geo_bin"] == geo_bin).sum() if "geo_bin" in df.columns else 1

    return pd.DataFrame([{
        "event_type": event_type,
        "event_cause_grouped": cause_grouped,
        "corridor_grouped": corridor_grouped,
        "veh_type_clean": veh_clean,
        "latitude": lat, "longitude": lon,
        "hour": hour,
        "day_of_week": DOW_MAP.get(dow, 3),
        "month": 3,
        "is_weekend": 1 if DOW_MAP.get(dow, 3) >= 5 else 0,
        "is_peak": 1 if hour in [8, 9, 10, 17, 18, 19] else 0,
        "geo_density": geo_density,
        "corridor_incident_count": corr_incidents,
        "corridor_closure_rate": corr_closure,
        "corridor_high_priority_rate": corr_priority,
    }])


def predict_incident(cause, event_type, corridor, hour, dow, veh_type):
    """Run all 3 ML models and return predictions."""
    severity_m, closure_m, resolution_m, le_dict, fc = load_ml_models()
    X = build_feature_row(cause, event_type, corridor, hour, dow, veh_type)
    feature_cols = fc["all_features"]
    X_model = X[feature_cols]

    sev_pred = int(severity_m.predict(X_model)[0])
    sev_prob = float(severity_m.predict_proba(X_model)[0][1])

    X_cl = X_model.copy()
    for col in fc["categorical_features"]:
        X_cl[col] = le_dict[col].transform(X_cl[col].astype(str))
    closure_prob = float(closure_m.predict(X_cl.values)[0])

    res_log = float(resolution_m.predict(X_model)[0])
    res_mins = float(np.expm1(res_log))

    return {
        "severity": "HIGH" if sev_pred == 1 else "LOW",
        "severity_prob": sev_prob if sev_pred == 1 else 1 - sev_prob,
        "closure_prob": closure_prob,
        "resolution_mins": res_mins,
        "hist_closure": float(df[df["event_cause"] == cause]["requires_road_closure"].mean()) if len(df[df["event_cause"] == cause]) else 0,
    }


def explain_prediction(cause, corridor, hour, dow, closure_prob, severity):
    """SHAP-like rule-based explanation of prediction drivers."""
    factors = []
    cause_data = df[df["event_cause"] == cause]
    hist_closure = cause_data["requires_road_closure"].mean() if len(cause_data) else 0
    cause_label = CAUSE_LABELS.get(cause, cause.replace("_", " ").title())

    if hist_closure > 0.15:
        factors.append(("event_cause", f"{cause_label} historically causes road closures in {hist_closure:.0%} of cases", +0.25))
    elif hist_closure > 0.05:
        factors.append(("event_cause", f"{cause_label} has moderate closure risk ({hist_closure:.0%})", +0.10))

    if hour in [8, 9, 10, 17, 18, 19]:
        factors.append(("peak_hour", f"Peak hour ({hour}:00) increases congestion and closure likelihood", +0.15))
    elif hour in [12, 13, 14]:
        factors.append(("midday", f"Midday hour ({hour}:00) sees elevated incident density", +0.08))

    corr_row = corridor_risk[corridor_risk["corridor"] == corridor]
    if len(corr_row):
        cr = corr_row.iloc[0]
        if cr["closure_rate"] > 0.08:
            factors.append(("corridor", f"{corridor} has high historical closure rate ({cr['closure_rate']:.0%})", +0.20))
        if cr["risk_score"] > 0.35:
            factors.append(("corridor_risk", f"{corridor} is a high-risk corridor (score {cr['risk_score']:.2f})", +0.12))

    if DOW_MAP.get(dow, 3) >= 5:
        factors.append(("weekend", "Weekend traffic patterns differ — lower volume but slower resolution", +0.05))

    high_impact_causes = ["accident", "vip_movement", "protest", "procession", "construction"]
    if cause in high_impact_causes:
        factors.append(("severity_driver", f"{cause_label} events typically require HIGH priority response", +0.18))

    if closure_prob > 0.3:
        summary = f"**Road closure probability is {closure_prob:.0%}** — primarily driven by "
        top = sorted(factors, key=lambda x: -abs(x[2]))[:3]
        summary += ", ".join(f[1].split("—")[0].strip() if "—" in f[1] else f[1] for f in top[:2])
        if hour in [8, 9, 10, 17, 18, 19]:
            summary += f", and it's **peak hour ({hour}:00)**"
    else:
        summary = f"Closure probability is **{closure_prob:.0%}** — lower risk due to "
        summary += f"{cause_label} typically not requiring full road closure on {corridor}"

    return summary, factors


def suggest_diversion(corridor, closure_prob):
    """Suggest alternative corridors when closure probability > 30%."""
    if closure_prob <= 0.3:
        return None
    row = corridor_risk[corridor_risk["corridor"] == corridor]
    if not len(row):
        return None
    lat, lon = row.iloc[0]["lat"], row.iloc[0]["lon"]
    others = corridor_risk[corridor_risk["corridor"] != corridor].copy()
    others["dist"] = np.sqrt((others["lat"] - lat) ** 2 + (others["lon"] - lon) ** 2)
    alts = others.sort_values(["risk_score", "dist"]).head(3)
    return alts[["corridor", "risk_score", "closure_rate", "total_incidents"]]


def risk_color(score):
    if score > 0.38:
        return "#fc5c65"
    if score > 0.33:
        return "#f7b731"
    return "#26de81"


def get_live_feed_html(critical_df):
    items = []
    for _, row in critical_df.iterrows():
        cause = str(row.get("event_cause", "")).replace("_", " ").title()
        corr = row.get("corridor", "Unknown")
        pri = row.get("priority", "High")
        items.append(
            f"🔴 <b>{cause}</b> on {corr} — Priority: {pri} | "
            f"Closure: {'Yes' if row.get('requires_road_closure') else 'No'}"
        )
    feed = " &nbsp;&nbsp;|&nbsp;&nbsp; ".join(items)
    return f'<div class="live-feed"><div class="live-feed-inner">{feed} &nbsp;&nbsp;|&nbsp;&nbsp; {feed}</div></div>'


def copilot_chart(question_lower):
    """Generate inline chart if question asks for visualization."""
    if "chart" not in question_lower and "graph" not in question_lower and "show me" not in question_lower:
        return None
    if any(w in question_lower for w in ["cause", "breakdown", "accident", "type"]):
        cause_counts = df["event_cause"].value_counts().head(10).reset_index()
        cause_counts.columns = ["cause", "count"]
        cause_counts["cause"] = cause_counts["cause"].str.replace("_", " ").str.title()
        fig = px.bar(cause_counts, x="count", y="cause", orientation="h",
                     color="count", color_continuous_scale="Viridis",
                     title="Incidents by Event Cause")
        fig.update_layout(template="plotly_dark", height=350,
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
        return fig
    if any(w in question_lower for w in ["hour", "time", "peak", "when"]):
        hourly = df.groupby("hour").size().reset_index(name="count")
        fig = px.area(hourly, x="hour", y="count", title="Hourly Incident Distribution",
                      color_discrete_sequence=["#667eea"])
        fig.update_layout(template="plotly_dark", height=350,
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        return fig
    if any(w in question_lower for w in ["corridor", "road", "route"]):
        top = corridor_risk.head(12)
        fig = px.bar(top, x="corridor", y="risk_score", color="risk_score",
                     color_continuous_scale="Reds", title="Top Corridors by Risk Score")
        fig.update_layout(template="plotly_dark", height=350,
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          coloraxis_showscale=False)
        return fig
    if any(w in question_lower for w in ["month", "trend", "over time"]):
        monthly = df.groupby("month").size().reset_index(name="count")
        month_names = {11: "Nov", 12: "Dec", 1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr"}
        monthly["month_label"] = monthly["month"].map(month_names)
        fig = px.line(monthly, x="month_label", y="count", markers=True,
                      title="Incident Trend (Last 6 Months)",
                      color_discrete_sequence=["#764ba2"])
        fig.update_layout(template="plotly_dark", height=350,
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        return fig
    return None


def get_copilot_answer(question, df_ref, ctx):
    """Structured retrieval copilot — rule-based answers."""
    question_lower = question.lower()

    if any(w in question_lower for w in ["breakdown", "accident", "tree", "protest", "construction", "vip"]):
        for cause in df_ref["event_cause"].unique():
            if cause.replace("_", " ") in question_lower or cause in question_lower:
                cause_data = df_ref[df_ref["event_cause"] == cause]
                total = len(cause_data)
                closure_rate = cause_data["requires_road_closure"].mean()
                high_prio = cause_data["priority_binary"].mean()
                median_res = cause_data["resolution_minutes"].median()
                resources = estimate_resources(cause, "High" if high_prio > 0.5 else "Low", closure_rate)
                top_corridors = cause_data["corridor"].value_counts().head(3)
                answer = f"""### Analysis: {cause.replace('_', ' ').title()} Incidents

**Historical Data:** {total} incidents in our database

| Metric | Value |
|---|---|
| 🔴 Road Closure Probability | {closure_rate:.0%} |
| ⚡ High Priority Rate | {high_prio:.0%} |
| ⏱️ Median Resolution Time | {median_res:.0f} minutes |

**Top Corridors Affected:**
"""
                for corr, count in top_corridors.items():
                    answer += f"- {corr}: {count} incidents\n"
                answer += f"""
**Recommended Resources:**
- 👮 Officers: {resources['officers']}
- 🚧 Barricades: {resources['barricades']}
- 🚛 Tow Truck: {'Yes' if resources['tow_truck'] else 'No'}
- 🚑 Ambulance: {'Yes' if resources['ambulance'] else 'No'}
"""
                return answer

    if any(w in question_lower for w in ["police", "station", "fastest", "resolve"]):
        ps = df_ref[df_ref["resolution_minutes"].notna()].groupby("police_station").agg(
            median_mins=("resolution_minutes", "median"),
            count=("id", "count"),
        ).reset_index()
        ps = ps[ps["count"] >= 10].sort_values("median_mins").head(8)
        answer = "### Fastest Police Stations (Median Resolution)\n\n| Station | Median Resolution | Incidents Handled |\n|---|---|---|\n"
        for _, row in ps.iterrows():
            answer += f"| {row['police_station']} | {row['median_mins']:.0f} min | {int(row['count'])} |\n"
        return answer

    if any(w in question_lower for w in ["risk", "dangerous", "worst", "hotspot", "highest"]):
        top5 = corridor_risk.head(5)
        answer = "### Highest Risk Corridors\n\n| Rank | Corridor | Risk Score | Incidents | Closure Rate |\n|---|---|---|---|---|\n"
        for i, (_, row) in enumerate(top5.iterrows()):
            answer += f"| {i+1} | {row['corridor']} | {row['risk_score']:.3f} | {int(row['total_incidents'])} | {row['closure_rate']:.0%} |\n"
        return answer

    if any(w in question_lower for w in ["hour", "time", "peak", "when", "morning", "evening"]):
        hourly = df_ref.groupby("hour").size()
        peak_hour = hourly.idxmax()
        return f"""### Temporal Pattern Analysis

**Peak incident hour:** {peak_hour}:00 ({hourly.max()} incidents)

| Time Period | Incidents | % of Total |
|---|---|---|
| Morning (6-10) | {hourly[6:10].sum()} | {hourly[6:10].sum()/len(df_ref):.0%} |
| Midday (10-14) | {hourly[10:14].sum()} | {hourly[10:14].sum()/len(df_ref):.0%} |
| Evening (14-20) | {hourly[14:20].sum()} | {hourly[14:20].sum()/len(df_ref):.0%} |
| Night (20-6) | {hourly[20:].sum() + hourly[:6].sum()} | {(hourly[20:].sum() + hourly[:6].sum())/len(df_ref):.0%} |

**Weekend vs Weekday:** Weekend = {df_ref[df_ref['is_weekend']==1].shape[0]} ({df_ref[df_ref['is_weekend']==1].shape[0]/len(df_ref):.0%})
"""

    if any(w in question_lower for w in ["corridor", "road", "route"]):
        for _, row in corridor_risk.iterrows():
            if row["corridor"].lower() in question_lower:
                cause_dist = df_ref[df_ref["corridor"] == row["corridor"]]["event_cause"].value_counts().head(5)
                answer = f"""### Corridor Intelligence: {row['corridor']}

| Metric | Value |
|---|---|
| Total Incidents | {int(row['total_incidents'])} |
| Risk Score | {row['risk_score']:.3f} |
| Road Closure Rate | {row['closure_rate']:.0%} |
| High Priority Rate | {row['high_priority_pct']:.0%} |
| Avg Resolution | {row['avg_resolution_mins']:.0f} min |

**Top Incident Causes:**
"""
                for c, count in cause_dist.items():
                    answer += f"- {c}: {count}\n"
                return answer

    return f"""### NammaTraffic Intelligence Summary

I have access to **{ctx['total_incidents']:,}** historical traffic incidents across **{ctx['corridors']}** corridors and **{ctx['police_stations']}** police stations.

**Try asking me:**
- "What is the impact of a vehicle breakdown?"
- "Which corridors are highest risk?"
- "Show me a chart of incidents by cause"
- "Which police station resolves incidents fastest?"
- "What happens during peak hours?"
"""


def call_llm(question, ctx, api_key, provider):
    """Optional LLM integration via REST API."""
    context_str = json.dumps({
        "total_incidents": ctx["total_incidents"],
        "corridors": ctx["corridors"],
        "police_stations": ctx["police_stations"],
        "top_causes": ctx.get("cause_distribution", [])[:5],
        "peak_hours": sorted(ctx.get("hourly_distribution", []), key=lambda x: -x["count"])[:3],
    }, indent=2, default=str)

    system_prompt = (
        "You are NammaTraffic AI Copilot for Bengaluru traffic operations. "
        "Answer concisely using the provided historical context. "
        "Use bullet points and include specific numbers when available.\n\n"
        f"Context:\n{context_str}"
    )

    try:
        if provider == "OpenAI":
            payload = json.dumps({
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question},
                ],
                "max_tokens": 600,
            }).encode()
            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=payload,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"]

        if provider == "Gemini":
            url = (
                f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"gemini-2.0-flash:generateContent?key={api_key}"
            )
            payload = json.dumps({
                "contents": [{"parts": [{"text": f"{system_prompt}\n\nUser: {question}"}]}],
            }).encode()
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
            return data["candidates"][0]["content"]["parts"][0]["text"]
    except (urllib.error.URLError, KeyError, IndexError, json.JSONDecodeError) as e:
        return f"⚠️ LLM call failed ({e}). Falling back to rule-based retrieval."
    return None


# ===================== SIDEBAR =====================
if DATA_LOADED:
    with st.sidebar:
        st.markdown('<p class="header-gradient">🚦 NammaTraffic</p>', unsafe_allow_html=True)
        st.caption("Bengaluru Traffic Incident Intelligence & Command Platform")
        st.markdown("---")

        page = st.radio("**Command Center**", [
            "📊 Operations Dashboard",
            "🗺️ GIS Risk Map",
            "🔍 Incident Explorer",
            "🧠 AI Traffic Copilot",
            "📈 ML Model Performance",
            "🔮 Incident Predictor",
        ])

        st.markdown("---")
        st.markdown("**Quick Stats**")
        st.metric("Total Incidents", f"{len(df):,}")
        st.metric("Active", f"{(df['status'] == 'active').sum():,}")
        st.metric("Road Closures", f"{df['requires_road_closure'].sum():,}")
        st.markdown("---")
        st.caption("Flipkart Gridlock 2.0 | Event-Driven Congestion")


# ===================== PAGE: OPERATIONS DASHBOARD =====================
if DATA_LOADED and page == "📊 Operations Dashboard":
    st.markdown("## 📊 Operations Command Dashboard")
    st.caption("Real-time traffic incident intelligence for Bengaluru")

    critical = df[(df["priority"] == "High") | (df["requires_road_closure"] == 1)].tail(12)
    st.markdown("#### 🔴 Live Critical Incident Feed")
    st.markdown(get_live_feed_html(critical), unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)
    active = (df["status"] == "active").sum()
    closure_rate = df["requires_road_closure"].mean()
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(df):,}</div><div class="metric-label">Total Incidents</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{df["requires_road_closure"].sum():,}</div><div class="metric-label">Road Closures</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{closure_rate:.0%}</div><div class="metric-label">Closure Rate</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{df["resolution_minutes"].median():.0f}m</div><div class="metric-label">Median Resolution</div></div>', unsafe_allow_html=True)
    with col5:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{active}</div><div class="metric-label">Active Now</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### Incidents by Cause")
        cause_counts = df["event_cause"].value_counts().head(10)
        fig = px.bar(x=cause_counts.values, y=cause_counts.index, orientation="h",
                     color=cause_counts.values, color_continuous_scale="Plasma",
                     labels={"x": "Count", "y": "Event Cause"})
        fig.update_layout(template="plotly_dark", height=400,
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          showlegend=False, coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("### Hourly Incident Distribution")
        hourly = df.groupby("hour").size().reset_index(name="count")
        fig = px.area(hourly, x="hour", y="count", color_discrete_sequence=["#667eea"],
                      labels={"hour": "Hour of Day", "count": "Incidents"})
        fig.update_layout(template="plotly_dark", height=400,
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🚨 Corridor Risk Ranking")
    risk_display = corridor_risk.head(15)[["corridor", "total_incidents", "closure_rate", "high_priority_pct", "risk_score"]].copy()
    risk_display.columns = ["Corridor", "Incidents", "Closure Rate", "High Priority %", "Risk Score"]
    risk_display["Closure Rate"] = risk_display["Closure Rate"].apply(lambda x: f"{x:.0%}")
    risk_display["High Priority %"] = risk_display["High Priority %"].apply(lambda x: f"{x:.0%}")
    risk_display["Risk Score"] = risk_display["Risk Score"].apply(lambda x: f"{x:.3f}")
    st.dataframe(risk_display, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### 📚 Post-Event Learning & Analytics")
    ana_col1, ana_col2 = st.columns(2)

    with ana_col1:
        st.markdown("#### Fastest Police Stations (Median Resolution)")
        ps = df[df["resolution_minutes"].notna()].groupby("police_station").agg(
            median_mins=("resolution_minutes", "median"), count=("id", "count"),
        ).reset_index()
        ps = ps[ps["count"] >= 15].sort_values("median_mins").head(10)
        fig_ps = px.bar(ps, x="median_mins", y="police_station", orientation="h",
                        color="median_mins", color_continuous_scale="Greens",
                        labels={"median_mins": "Median Minutes", "police_station": "Station"})
        fig_ps.update_layout(template="plotly_dark", height=380,
                             paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                             yaxis=dict(autorange="reversed"), coloraxis_showscale=False,
                             title="Lower is Better")
        st.plotly_chart(fig_ps, use_container_width=True)

    with ana_col2:
        st.markdown("#### Incident Trend (Nov 2023 – Apr 2024)")
        monthly = df.groupby("month").agg(
            incidents=("id", "count"),
            closure_rate=("requires_road_closure", "mean"),
        ).reset_index()
        month_names = {11: "Nov '23", 12: "Dec '23", 1: "Jan '24", 2: "Feb '24", 3: "Mar '24", 4: "Apr '24"}
        monthly["month_label"] = monthly["month"].map(month_names)
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(x=monthly["month_label"], y=monthly["incidents"],
                                   name="Incidents", marker_color="#667eea"))
        fig_trend.add_trace(go.Scatter(x=monthly["month_label"], y=monthly["closure_rate"] * 100,
                                       name="Closure Rate %", yaxis="y2", line=dict(color="#fc5c65", width=3)))
        fig_trend.update_layout(
            template="plotly_dark", height=380,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(title="Incidents"), yaxis2=dict(title="Closure %", overlaying="y", side="right"),
            title="3-Month Incident & Closure Trend",
        )
        st.plotly_chart(fig_trend, use_container_width=True)


# ===================== PAGE: GIS RISK MAP =====================
elif DATA_LOADED and page == "🗺️ GIS Risk Map":
    import folium
    from streamlit_folium import st_folium
    from folium.plugins import HeatMap, MarkerCluster

    st.markdown("## 🗺️ Geospatial Risk Intelligence Map")

    map_type = st.radio("Map Layer", ["🔥 Heatmap", "📍 Incident Markers", "⭕ Hotspot Clusters"], horizontal=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        cause_filter = st.multiselect("Event Cause", df["event_cause"].unique().tolist())
    with col2:
        priority_filter = st.multiselect("Priority", ["High", "Low"])
    with col3:
        closure_filter = st.selectbox("Road Closure", ["All", "Yes", "No"])
    with col4:
        show_corridors = st.toggle("🛣️ High-Risk Corridors", value=False)

    st.markdown("##### ⏱️ Time-Lapse Playback — Filter by Hour of Day")
    hour_range = st.slider("Hour Range", 0, 23, (0, 23), label_visibility="collapsed")
    selected_hour = st.select_slider("Scrub to Hour", options=list(range(24)), value=17,
                                     format_func=lambda h: f"{h:02d}:00")

    df_map = df.copy()
    if cause_filter:
        df_map = df_map[df_map["event_cause"].isin(cause_filter)]
    if priority_filter:
        df_map = df_map[df_map["priority"].isin(priority_filter)]
    if closure_filter == "Yes":
        df_map = df_map[df_map["requires_road_closure"] == 1]
    elif closure_filter == "No":
        df_map = df_map[df_map["requires_road_closure"] == 0]
    df_map = df_map[(df_map["hour"] >= hour_range[0]) & (df_map["hour"] <= hour_range[1])]
    if selected_hour is not None:
        df_hour = df_map[df_map["hour"] == selected_hour]
    else:
        df_hour = df_map

    st.caption(f"Showing **{len(df_hour):,}** incidents at **{selected_hour:02d}:00** (range {hour_range[0]:02d}:00–{hour_range[1]:02d}:00)")

    m = folium.Map(location=[12.9716, 77.5946], zoom_start=12, tiles="CartoDB dark_matter")

    legend_html = """
    <div style="position:fixed;bottom:30px;left:10px;z-index:9999;background:#1a1f2e;
                border:1px solid #667eea;border-radius:8px;padding:12px;font-size:12px;color:#fff;">
    <b>Map Legend</b><br>
    <span style="color:#fc5c65;">●</span> High Risk Corridor<br>
    <span style="color:#f7b731;">●</span> Medium Risk<br>
    <span style="color:#26de81;">●</span> Low Risk Hotspot<br>
    <span style="color:#667eea;">●</span> High Priority Incident<br>
    <span style="color:#45aaf2;">●</span> Low Priority Incident
    </div>"""
    m.get_root().html.add_child(folium.Element(legend_html))

    if map_type == "🔥 Heatmap":
        heat_data = df_hour[["latitude", "longitude"]].dropna().values.tolist()
        if heat_data:
            HeatMap(heat_data, radius=15, blur=20, max_zoom=15,
                    gradient={0.2: "#2196F3", 0.4: "#4CAF50", 0.6: "#FFC107", 0.8: "#FF5722", 1: "#D32F2F"}).add_to(m)

    elif map_type == "📍 Incident Markers":
        mc = MarkerCluster()
        sample = df_hour.sample(min(500, len(df_hour)), random_state=42) if len(df_hour) else df_hour
        for _, row in sample.iterrows():
            color = "red" if row.get("priority") == "High" else "blue"
            icon_name = "warning-sign" if row.get("requires_road_closure") == 1 else "info-sign"
            popup_html = (
                f"<b>{row.get('event_cause', 'N/A').replace('_', ' ').title()}</b><br>"
                f"Priority: {row.get('priority', 'N/A')}<br>"
                f"Corridor: {row.get('corridor', 'N/A')}<br>"
                f"Hour: {row.get('hour', 'N/A')}:00<br>"
                f"Road Closure: {'Yes' if row.get('requires_road_closure') == 1 else 'No'}"
            )
            folium.Marker(
                [row["latitude"], row["longitude"]],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color=color, icon=icon_name, prefix="glyphicon"),
            ).add_to(mc)
        mc.add_to(m)

    elif map_type == "⭕ Hotspot Clusters":
        for _, cluster in hotspot_clusters.iterrows():
            radius = max(200, cluster["incident_count"] * 15)
            color = "#fc5c65" if cluster["closure_rate"] > 0.1 else "#f7b731" if cluster["incident_count"] > 50 else "#26de81"
            folium.Circle(
                [cluster["centroid_lat"], cluster["centroid_lon"]],
                radius=radius,
                popup=(
                    f"<b>Cluster {int(cluster['hotspot_cluster'])}</b><br>"
                    f"Incidents: {int(cluster['incident_count'])}<br>"
                    f"Closure Rate: {cluster['closure_rate']:.0%}<br>"
                    f"Top Cause: {cluster['top_cause']}"
                ),
                color=color, fill=True, fill_opacity=0.35, weight=2,
                tooltip=f"Hotspot #{int(cluster['hotspot_cluster'])} — {int(cluster['incident_count'])} incidents",
            ).add_to(m)
            folium.CircleMarker(
                [cluster["centroid_lat"], cluster["centroid_lon"]],
                radius=8, color=color, fill=True, fill_opacity=0.9,
                popup=f"Hotspot #{int(cluster['hotspot_cluster'])}",
            ).add_to(m)

    if show_corridors:
        for _, cr in corridor_risk.head(12).iterrows():
            pts = df[df["corridor"] == cr["corridor"]][["latitude", "longitude"]].dropna()
            if len(pts) < 3:
                continue
            coords = pts.sample(min(40, len(pts)), random_state=42).sort_values("latitude").values.tolist()
            color = risk_color(cr["risk_score"])
            folium.PolyLine(
                coords, color=color, weight=4, opacity=0.75,
                popup=f"<b>{cr['corridor']}</b><br>Risk: {cr['risk_score']:.3f}<br>Closure: {cr['closure_rate']:.0%}",
                tooltip=cr["corridor"],
            ).add_to(m)

    st_folium(m, width=None, height=600, use_container_width=True)


# ===================== PAGE: INCIDENT EXPLORER =====================
elif DATA_LOADED and page == "🔍 Incident Explorer":
    st.markdown("## 🔍 Incident Explorer & Similar Incident Search")

    col1, col2 = st.columns([2, 1])
    with col1:
        search_corridor = st.selectbox("Select Corridor", ["All"] + sorted(df["corridor"].dropna().unique().tolist()))
    with col2:
        search_cause = st.selectbox("Select Cause", ["All"] + sorted(df["event_cause"].dropna().unique().tolist()))

    df_filtered = df.copy()
    if search_corridor != "All":
        df_filtered = df_filtered[df_filtered["corridor"] == search_corridor]
    if search_cause != "All":
        df_filtered = df_filtered[df_filtered["event_cause"] == search_cause]

    display_cols = ["id", "event_cause", "priority", "corridor", "requires_road_closure", "status", "police_station", "description"]
    available_cols = [c for c in display_cols if c in df_filtered.columns]

    st.markdown(f"### {len(df_filtered):,} Incidents Found")
    st.dataframe(df_filtered[available_cols].head(100), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### 🔗 Similar Incident Search")
    incident_id = st.selectbox("Select Incident ID", df_filtered["id"].head(200).tolist())

    if st.button("🔍 Find Similar Incidents", type="primary"):
        idx = df[df["id"] == incident_id].index[0]
        similar_idx, scores = find_similar_incidents(idx, top_k=5)
        source = df.iloc[idx]
        st.markdown(
            f'<div class="incident-card"><b>Source: {source["id"]}</b><br>'
            f'Cause: {source["event_cause"]} | Priority: {source["priority"]} | '
            f'Corridor: {source["corridor"]}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("#### Top 5 Similar Incidents")
        for rank, (s_idx, score) in enumerate(zip(similar_idx, scores)):
            row = df.iloc[s_idx]
            res_str = f"{row['resolution_minutes']:.0f} min" if pd.notna(row.get("resolution_minutes")) else "N/A"
            st.markdown(
                f'<div class="incident-card"><b>#{rank+1} — {row["id"]}</b> (Similarity: {score:.2%})<br>'
                f'Cause: {row["event_cause"]} | Corridor: {row["corridor"]} | Resolution: {res_str}<br>'
                f'<small>{row.get("description", "")}</small></div>',
                unsafe_allow_html=True,
            )


# ===================== PAGE: AI COPILOT =====================
elif DATA_LOADED and page == "🧠 AI Traffic Copilot":
    st.markdown("## 🧠 AI Traffic Copilot")
    st.caption("Retrieval over 8,173 historical records · Optional LLM enhancement")

    with st.expander("⚙️ LLM Settings (Optional)"):
        llm_provider = st.selectbox("Provider", ["Rule-Based (Default)", "OpenAI", "Gemini"])
        api_key = st.text_input("API Key", type="password", help="Leave blank to use rule-based retrieval")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    quick_cols = st.columns(4)
    quick_qs = [
        ("🚧 Breakdown Impact", "What is the impact of a vehicle breakdown?"),
        ("⚠️ Risk Corridors", "Which corridors are highest risk?"),
        ("📊 Chart by Cause", "Show me a chart of incidents by cause"),
        ("👮 Fastest Stations", "Which police station resolves incidents fastest?"),
    ]
    for col, (label, q) in zip(quick_cols, quick_qs):
        with col:
            if st.button(label, use_container_width=True):
                st.session_state.pending_q = q

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("chart_query"):
                chart = copilot_chart(msg["chart_query"])
                if chart:
                    st.plotly_chart(chart, use_container_width=True)

    prompt = st.session_state.pop("pending_q", None)
    if prompt is None:
        prompt = st.chat_input("Ask NammaTraffic Copilot...")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                chart = copilot_chart(prompt.lower())
                if llm_provider != "Rule-Based (Default)" and api_key:
                    answer = call_llm(prompt, copilot_ctx, api_key, llm_provider)
                    if answer and answer.startswith("⚠️"):
                        answer = get_copilot_answer(prompt, df, copilot_ctx)
                else:
                    answer = get_copilot_answer(prompt, df, copilot_ctx)

                st.markdown(answer)
                if chart:
                    st.plotly_chart(chart, use_container_width=True)

                chart_query = prompt.lower() if chart else None
                st.session_state.messages.append({"role": "assistant", "content": answer, "chart_query": chart_query})

    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()


# ===================== PAGE: ML PERFORMANCE =====================
elif DATA_LOADED and page == "📈 ML Model Performance":
    st.markdown("## 📈 Machine Learning Model Performance")
    st.caption("Three production-grade models trained on 8,173 Bengaluru traffic incidents.")

    for model_name, model_data in model_perf.items():
        display_name = model_name.replace("_", " ").title()
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(
                f'<div class="metric-card"><div class="metric-value">{model_data["cv_mean"]}</div>'
                f'<div class="metric-label">{model_data["metric"]} (5-Fold CV)</div></div>',
                unsafe_allow_html=True,
            )
            st.markdown(f"**Model:** {model_data['type']}")
            st.markdown(f"**Target:** {model_data['target']}")
            st.markdown(f"**Std Dev:** ±{model_data['cv_std']}")
        with col2:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=[f"Fold {i+1}" for i in range(5)], y=model_data["fold_scores"],
                marker_color=["#667eea", "#764ba2", "#667eea", "#764ba2", "#667eea"],
                text=[f"{s:.4f}" for s in model_data["fold_scores"]], textposition="outside",
            ))
            fig.add_hline(y=model_data["cv_mean"], line_dash="dash", line_color="#f7b731",
                          annotation_text=f"Mean: {model_data['cv_mean']}")
            fig.update_layout(title=f"{display_name} — Fold-wise {model_data['metric']}",
                              template="plotly_dark", height=300,
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              yaxis_title=model_data["metric"])
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("---")


# ===================== PAGE: INCIDENT PREDICTOR =====================
elif DATA_LOADED and page == "🔮 Incident Predictor":
    st.markdown("## 🔮 New Incident Prediction")
    st.caption("ML-powered severity, closure probability, resolution time & resource allocation")

    for k, v in [("pred_cause", "accident"), ("pred_event_type", "unplanned"),
                 ("pred_corridor", "Hosur Road"), ("pred_hour", 17),
                 ("pred_dow", "Friday"), ("pred_veh", "unknown")]:
        if k not in st.session_state:
            st.session_state[k] = v

    st.markdown("#### 🎬 Demo Scenarios — Click to Load")
    scen_cols = st.columns(3)
    for col, (label, params) in zip(scen_cols, DEMO_SCENARIOS.items()):
        with col:
            if st.button(label, use_container_width=True, key=f"demo_{label[:20]}"):
                st.session_state["pred_cause"] = params["cause"]
                st.session_state["pred_event_type"] = params["event_type"]
                st.session_state["pred_corridor"] = params["corridor"]
                st.session_state["pred_hour"] = params["hour"]
                st.session_state["pred_dow"] = params["dow"]
                st.session_state["pred_veh"] = params["veh"]
                st.rerun()

    col1, col2 = st.columns(2)
    causes = sorted(df["event_cause"].unique().tolist())
    corridors = sorted(df["corridor"].dropna().unique().tolist())
    veh_types = ["unknown"] + sorted(df["veh_type_clean"].dropna().unique().tolist())

    with col1:
        st.markdown("### Incident Details")
        pred_cause = st.selectbox("Event Cause", causes, key="pred_cause")
        pred_type = st.selectbox("Event Type", ["unplanned", "planned"], key="pred_event_type")
        pred_corridor = st.selectbox("Corridor", corridors, key="pred_corridor")
        pred_hour = st.slider("Hour of Day", 0, 23, key="pred_hour")
        pred_dow = st.selectbox("Day of Week", list(DOW_MAP.keys()), key="pred_dow")
        pred_veh = st.selectbox("Vehicle Type", veh_types, key="pred_veh")

    with col2:
        if st.button("⚡ Predict", type="primary", use_container_width=True):
            preds = predict_incident(pred_cause, pred_type, pred_corridor, pred_hour, pred_dow, pred_veh)
            severity = preds["severity"]
            closure_prob = preds["closure_prob"]
            median_res = preds["resolution_mins"]
            sev_conf = preds["severity_prob"]
            diversion_prob = max(closure_prob, preds["hist_closure"])
            resources = estimate_resources(pred_cause, severity.replace("HIGH", "High").replace("LOW", "Low"), diversion_prob)
            sev_class = "severity-high" if severity == "HIGH" else "severity-low"

            st.markdown("### 🎯 Prediction Results")
            st.markdown(
                f'<div class="incident-card"><h4>Severity: <span class="{sev_class}">{severity}</span></h4>'
                f'<p>Confidence: {sev_conf:.0%}</p></div>',
                unsafe_allow_html=True,
            )

            pcol1, pcol2 = st.columns(2)
            with pcol1:
                st.metric("🚧 Road Closure Probability", f"{closure_prob:.0%}")
                st.metric("⏱️ Est. Resolution Time", f"{median_res:.0f} min")
            with pcol2:
                st.metric("👮 Officers Needed", resources["officers"])
                st.metric("🚧 Barricades", resources["barricades"])

            st.markdown("### 🔍 Why This Prediction?")
            summary, factors = explain_prediction(pred_cause, pred_corridor, pred_hour, pred_dow, closure_prob, severity)
            st.info(summary)
            for _, desc, impact in sorted(factors, key=lambda x: -abs(x[2])):
                bar_width = min(int(abs(impact) * 200), 100)
                st.markdown(
                    f'<div class="explain-bar">{"🔺" if impact > 0 else "🔻"} {desc} '
                    f'<span style="float:right;color:#667eea;">{"+" if impact>0 else ""}{impact:.0%}</span></div>',
                    unsafe_allow_html=True,
                )

            if diversion_prob > 0.3:
                st.markdown("### 🛣️ Diversion Recommendation")
                alts = suggest_diversion(pred_corridor, diversion_prob)
                if alts is not None and len(alts):
                    st.warning(
                        f"Operational closure risk **{diversion_prob:.0%}** exceeds 30% threshold on "
                        f"**{pred_corridor}** (ML: {closure_prob:.0%}, historical: {preds['hist_closure']:.0%}). "
                        f"Recommend diverting traffic:"
                    )
                    for _, alt in alts.iterrows():
                        st.markdown(
                            f"- **{alt['corridor']}** — Risk score {alt['risk_score']:.3f}, "
                            f"closure rate {alt['closure_rate']:.0%} ({int(alt['total_incidents'])} historical incidents)"
                        )

            st.markdown("### 📋 Resource Recommendation")
            rec = [f"- 👮 Deploy **{resources['officers']} officers**", f"- 🚧 Set up **{resources['barricades']} barricades**"]
            if resources["tow_truck"]:
                rec.append("- 🚛 **Dispatch tow truck**")
            if resources["ambulance"]:
                rec.append("- 🚑 **Alert ambulance**")
            st.markdown("\n".join(rec))

            st.markdown("### 🔗 Similar Past Incidents")
            cause_data = df[df["event_cause"] == pred_cause]
            for _, row in cause_data.head(3).iterrows():
                res_str = f"{row['resolution_minutes']:.0f} min" if pd.notna(row.get("resolution_minutes")) else "N/A"
                st.markdown(f"- **{row['id']}** — {row['corridor']}, Resolution: {res_str}")


# ===================== FOOTER =====================
if DATA_LOADED:
    st.markdown("---")
    st.markdown(
        "<center><small>NammaTraffic v1.0 | Flipkart Gridlock Hackathon 2.0 | "
        "Event-Driven Congestion | Built for Bengaluru 🚦</small></center>",
        unsafe_allow_html=True,
    )
