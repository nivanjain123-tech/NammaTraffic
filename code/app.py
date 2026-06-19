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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    .stApp { background-color: #0e1117; font-family: 'Inter', sans-serif; }

    .metric-card {
        background: linear-gradient(135deg, #1a1f2e 0%, #252b3b 100%);
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 20px;
        margin: 8px 0;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
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
        transition: border-color 0.2s;
    }
    .incident-card:hover { border-left-color: #764ba2; }

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
        position: relative;
    }
    .live-feed::before {
        content: '🔴 LIVE';
        position: absolute; left: 8px; top: 50%; transform: translateY(-50%);
        background: #fc5c65; color: white; padding: 2px 8px; border-radius: 4px;
        font-size: 0.7em; font-weight: 700; z-index: 2;
        animation: pulse-badge 2s infinite;
    }
    @keyframes pulse-badge {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    .live-feed-inner {
        display: inline-block;
        padding-left: 60px;
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

    .hero-card {
        background: linear-gradient(135deg, rgba(102,126,234,0.12) 0%, rgba(118,75,162,0.08) 100%);
        border: 1px solid rgba(102,126,234,0.3);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
    }
    .hero-card h3 { margin: 0 0 8px; color: #e2e8f0; }
    .hero-card p { color: #a0aec0; margin: 4px 0; font-size: 0.95em; }

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

    is_peak = 1 if hour in [8, 9, 10, 17, 18, 19] else 0
    cause_peak = f"{cause_grouped}_{is_peak}"

    return pd.DataFrame([{
        "event_type": event_type,
        "event_cause_grouped": cause_grouped,
        "corridor_grouped": corridor_grouped,
        "veh_type_clean": veh_clean,
        "cause_peak_interaction": cause_peak,
        "latitude": lat, "longitude": lon,
        "hour": hour,
        "day_of_week": DOW_MAP.get(dow, 3),
        "month": 3,
        "is_weekend": 1 if DOW_MAP.get(dow, 3) >= 5 else 0,
        "is_peak": is_peak,
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

    if "compare" in question_lower and any(w in question_lower for w in ["corridor", "road", "vs", "versus"]):
        found = []
        for _, row in corridor_risk.iterrows():
            if row['corridor'].lower() in question_lower:
                found.append(row)
        if len(found) >= 2:
            answer = "### Corridor Comparison\n\n| Metric | " + " | ".join(f['corridor'] for f in found[:2]) + " |\n|---|---|---|\n"
            for metric in ['total_incidents', 'closure_rate', 'high_priority_pct', 'risk_score']:
                label = metric.replace('_', ' ').title()
                vals = []
                for f in found[:2]:
                    v = f[metric]
                    vals.append(f"{v:.0%}" if 'rate' in metric or 'pct' in metric else (f"{v:.3f}" if 'score' in metric else str(int(v))))
                answer += f"| {label} | " + " | ".join(vals) + " |\n"
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
            "📑 Project Documentation",
        ])

        st.markdown("---")
        st.markdown("**Quick Stats**")
        st.metric("Total Incidents", f"{len(df):,}")
        st.metric("Active", f"{(df['status'] == 'active').sum():,}")
        st.metric("Road Closures", f"{df['requires_road_closure'].sum():,}")
        st.markdown("---")
        st.caption("Flipkart Gridlock 2.0 | Event-Driven Congestion")


def compute_corridor_risk(data):
    if len(data) == 0:
        return pd.DataFrame(columns=["corridor", "total_incidents", "closure_rate", "high_priority_pct", "risk_score"])
    
    corr_risk = data.groupby("corridor").agg(
        total_incidents=("id", "count"),
        closure_rate=("requires_road_closure", "mean"),
        high_priority_pct=("priority_binary", "mean"),
        lat=("latitude", "mean"),
        lon=("longitude", "mean")
    ).reset_index()
    
    max_incidents = corr_risk["total_incidents"].max()
    max_incidents = max_incidents if max_incidents > 0 else 1
    
    corr_risk["risk_score"] = (
        0.4 * corr_risk["total_incidents"] / max_incidents +
        0.3 * corr_risk["closure_rate"] +
        0.3 * corr_risk["high_priority_pct"]
    )
    return corr_risk.sort_values("risk_score", ascending=False)


# ===================== PAGE: OPERATIONS DASHBOARD =====================
if DATA_LOADED and page == "📊 Operations Dashboard":
    st.markdown("## 📊 Operations Command Dashboard")

    st.markdown("""
    <div class="hero-card">
        <h3>🚦 NammaTraffic — Bengaluru Traffic Incident Intelligence & Command Platform</h3>
        <p>A proactive AI-powered command center that transforms how Bengaluru manages traffic incidents.
        Instead of reactive phone-based dispatching, NammaTraffic <b>predicts</b> severity, <b>estimates</b>
        road closure probability, <b>recommends</b> resources, and <b>learns</b> from every resolved incident.</p>
        <p>📊 <b>8,173</b> real incidents · 🗺️ <b>22</b> corridors · 🤖 <b>3</b> ML models · 🧠 AI Copilot</p>
    </div>
    """, unsafe_allow_html=True)

    # Filter controls
    zones_list = ["All Zones"] + sorted([z for z in df["zone"].dropna().unique() if str(z).strip() != ""])
    selected_zone = st.selectbox("🎯 Filter Platform by Bengaluru Police Zone", zones_list)
    
    # Filter dataset
    if selected_zone != "All Zones":
        df_dash = df[df["zone"] == selected_zone].copy()
        corr_risk_dash = compute_corridor_risk(df_dash)
    else:
        df_dash = df.copy()
        corr_risk_dash = corridor_risk.copy()

    critical = df_dash[(df_dash["priority"] == "High") | (df_dash["requires_road_closure"] == 1)].tail(12)
    st.markdown("#### 🔴 Live Critical Incident Feed")
    st.markdown(get_live_feed_html(critical), unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)
    active = (df_dash["status"] == "active").sum()
    closure_rate = df_dash["requires_road_closure"].mean()
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(df_dash):,}</div><div class="metric-label">Total Incidents</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{df_dash["requires_road_closure"].sum():,}</div><div class="metric-label">Road Closures</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{closure_rate:.0%}</div><div class="metric-label">Closure Rate</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{df_dash["resolution_minutes"].median():.0f}m</div><div class="metric-label">Median Resolution</div></div>', unsafe_allow_html=True)
    with col5:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{active}</div><div class="metric-label">Active Now</div></div>', unsafe_allow_html=True)

    # Dynamic Key Insights Card
    unplanned_dash = df_dash[df_dash["event_type"] == "unplanned"]
    evening_peak_incidents = len(unplanned_dash[unplanned_dash["hour"].isin([17, 18, 19])])
    total_unplanned = len(unplanned_dash) if len(unplanned_dash) > 0 else 1
    evening_peak_pct = (evening_peak_incidents / total_unplanned) * 100

    breakdowns_closure = len(df_dash[(df_dash["event_cause"] == "vehicle_breakdown") & (df_dash["requires_road_closure"] == 1)])
    total_closures = len(df_dash[df_dash["requires_road_closure"] == 1]) if len(df_dash[df_dash["requires_road_closure"] == 1]) > 0 else 1
    breakdown_closure_pct = (breakdowns_closure / total_closures) * 100

    top_risk_text = "N/A"
    if len(corr_risk_dash) > 0:
        top_risk_row = corr_risk_dash.iloc[0]
        top_risk_text = f"**{top_risk_row['corridor']}** (Risk Score: **{top_risk_row['risk_score']:.3f}**)"

    st.markdown(f"""
    <div class="hero-card" style="background: linear-gradient(135deg, #1b263b 0%, #0d1b2a 100%); border-color: #415a77; margin-top: 15px; margin-bottom: 25px;">
        <h4 style="color: #e0e1dd; margin-top: 0;">💡 Proactive Command Key Insights ({selected_zone})</h4>
        <ul style="color: #a3b18a; margin-bottom: 0; padding-left: 20px;">
            <li>🌙 <b>Evening Peak Congestion:</b> Evening peak hours (17:00–19:00) account for <b>{evening_peak_pct:.1f}%</b> of unplanned incidents.</li>
            <li>🚛 <b>Breakdown Hazard:</b> Vehicle breakdowns are responsible for <b>{breakdown_closure_pct:.1f}%</b> of all incidents requiring road closures.</li>
            <li>🚨 <b>Critical Path:</b> Highest risk corridor is {top_risk_text}.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### Incidents by Cause")
        cause_counts = df_dash["event_cause"].value_counts().head(10)
        fig = px.bar(x=cause_counts.values, y=cause_counts.index, orientation="h",
                     color=cause_counts.values, color_continuous_scale="Plasma",
                     labels={"x": "Count", "y": "Event Cause"})
        fig.update_layout(template="plotly_dark", height=400,
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          showlegend=False, coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, width="stretch")

    with col_right:
        st.markdown("### Hourly Incident Distribution")
        hourly = df_dash.groupby("hour").size().reset_index(name="count")
        fig = px.area(hourly, x="hour", y="count", color_discrete_sequence=["#667eea"],
                      labels={"hour": "Hour of Day", "count": "Incidents"})
        fig.update_layout(template="plotly_dark", height=400,
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, width="stretch")

    st.markdown("### 🚨 Corridor Risk Ranking")
    if len(corr_risk_dash) > 0:
        risk_display = corr_risk_dash.head(15)[["corridor", "total_incidents", "closure_rate", "high_priority_pct", "risk_score"]].copy()
        risk_display.columns = ["Corridor", "Incidents", "Closure Rate", "High Priority %", "Risk Score"]
        risk_display["Closure Rate"] = risk_display["Closure Rate"].apply(lambda x: f"{x:.0%}")
        risk_display["High Priority %"] = risk_display["High Priority %"].apply(lambda x: f"{x:.0%}")
        risk_display["Risk Score"] = risk_display["Risk Score"].apply(lambda x: f"{x:.3f}")
        st.dataframe(risk_display, width="stretch", hide_index=True)
    else:
        st.info("No corridors with incidents recorded in this zone.")

    # Zone-level breakdown donut
    st.markdown("---")
    col_zone, col_closure_cause = st.columns(2)
    with col_zone:
        st.markdown("### 🏙️ Incidents by Zone")
        zone_data = df_dash[df_dash['zone'].notna()]['zone'].value_counts().reset_index()
        zone_data.columns = ['Zone', 'Count']
        fig_zone = px.pie(zone_data, names='Zone', values='Count', hole=0.45,
                          color_discrete_sequence=px.colors.sequential.Plasma_r)
        fig_zone.update_layout(template='plotly_dark', height=350,
                               paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_zone, width="stretch")

    with col_closure_cause:
        st.markdown("### 🚧 Road Closure by Event Cause")
        cl_cause = df_dash.groupby('event_cause')['requires_road_closure'].mean().sort_values(ascending=False).head(10).reset_index()
        cl_cause.columns = ['Cause', 'Closure Rate']
        cl_cause['Cause'] = cl_cause['Cause'].str.replace('_', ' ').str.title()
        fig_cl = px.bar(cl_cause, x='Closure Rate', y='Cause', orientation='h',
                        color='Closure Rate', color_continuous_scale='Reds',
                        labels={'Closure Rate': 'Closure Probability'})
        fig_cl.update_layout(template='plotly_dark', height=350,
                             paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                             yaxis=dict(autorange='reversed'), coloraxis_showscale=False)
        fig_cl.update_traces(texttemplate='%{x:.0%}', textposition='outside')
        st.plotly_chart(fig_cl, width="stretch")

    st.markdown("---")
    st.markdown("### 📚 Post-Event Learning & Analytics")
    ana_col1, ana_col2 = st.columns(2)

    with ana_col1:
        st.markdown("#### Fastest Police Stations (Median Resolution)")
        ps = df_dash[df_dash["resolution_minutes"].notna()].groupby("police_station").agg(
            median_mins=("resolution_minutes", "median"), count=("id", "count"),
        ).reset_index()
        ps = ps[ps["count"] >= 15].sort_values("median_mins").head(10)
        if len(ps) > 0:
            fig_ps = px.bar(ps, x="median_mins", y="police_station", orientation="h",
                            color="median_mins", color_continuous_scale="Greens",
                            labels={"median_mins": "Median Minutes", "police_station": "Station"})
            fig_ps.update_layout(template="plotly_dark", height=380,
                                 paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                 yaxis=dict(autorange="reversed"), coloraxis_showscale=False,
                                 title="Lower is Better")
            st.plotly_chart(fig_ps, width="stretch")
        else:
            st.info("No police stations with >= 15 incidents in this zone.")

    with ana_col2:
        st.markdown("#### Incident Trend (Nov 2023 – Apr 2024)")
        monthly = df_dash.groupby("month").agg(
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
        st.plotly_chart(fig_trend, width="stretch")


# ===================== PAGE: GIS RISK MAP =====================
elif DATA_LOADED and page == "🗺️ GIS Risk Map":
    import folium
    from streamlit_folium import st_folium
    from folium.plugins import HeatMap, MarkerCluster

    st.markdown("## 🗺️ Geospatial Risk Intelligence Map")

    map_type = st.radio("Map Layer", ["🔥 Heatmap", "📍 Incident Markers", "⭕ Hotspot Clusters", "🔮 Next-Hour Predicted Hotspots"], horizontal=True)

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
    <style>
    @keyframes pulse {
        0% { transform: scale(0.8); opacity: 0.5; }
        50% { transform: scale(1.3); opacity: 1; }
        100% { transform: scale(0.8); opacity: 0.5; }
    }
    .pulsing-dot {
        background-color: #fc5c65;
        border-radius: 50%;
        border: 2px solid #ffffff;
        width: 14px;
        height: 14px;
        animation: pulse 1.2s infinite ease-in-out;
        display: inline-block;
    }
    </style>
    <div style="position:fixed;bottom:30px;left:10px;z-index:9999;background:#1a1f2e;
                border:1px solid #667eea;border-radius:8px;padding:12px;font-size:12px;color:#fff;">
    <b>Map Legend</b><br>
    <span class="pulsing-dot" style="vertical-align:middle;margin-right:5px;"></span> Recent Critical Incident (Pulse)<br>
    <span style="color:#fc5c65;font-size:16px;line-height:10px;">▬</span> High Risk Corridor<br>
    <span style="color:#f7b731;font-size:16px;line-height:10px;">▬</span> Medium Risk<br>
    <span style="color:#26de81;font-size:16px;line-height:10px;">▬</span> Low Risk Hotspot<br>
    <span style="color:#fc5c65;font-size:16px;line-height:10px;">●</span> Hotspot cent.<br>
    <span style="color:#667eea;font-size:16px;line-height:10px;">●</span> High Priority Incident<br>
    <span style="color:#45aaf2;font-size:16px;line-height:10px;">●</span> Low Priority Incident
    </div>"""
    m.get_root().html.add_child(folium.Element(legend_html))

    # Add pulsing markers for the top 5 most recent critical incidents
    recent_critical = df_hour[(df_hour["priority"] == "High") | (df_hour["requires_road_closure"] == 1)].tail(5)
    for _, row in recent_critical.iterrows():
        popup_html = (
            f"<b>🚨 RECENT CRITICAL: {row.get('event_cause', 'N/A').replace('_', ' ').title()}</b><br>"
            f"Corridor: {row.get('corridor', 'N/A')}<br>"
            f"Priority: {row.get('priority', 'N/A')}<br>"
            f"Road Closure: {'Yes' if row.get('requires_road_closure') == 1 else 'No'}"
        )
        folium.Marker(
            [row["latitude"], row["longitude"]],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.DivIcon(
                html='<div class="pulsing-dot" style="box-shadow: 0 0 12px #fc5c65;"></div>',
                icon_size=(14, 14),
                icon_anchor=(7, 7)
            )
        ).add_to(m)

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

    elif map_type == "🔮 Next-Hour Predicted Hotspots":
        st.info("🔮 Predicting spatial risk hotspots for the next hour based on corridor parameters and temporal trends...")
        next_hour = (selected_hour + 1) % 24
        
        # Run prediction for each corridor
        for _, cr in corridor_risk.iterrows():
            # Predict for the most common cause in this corridor
            corr_incidents_data = df[df["corridor"] == cr["corridor"]]
            if len(corr_incidents_data) == 0:
                continue
            top_cause = corr_incidents_data["event_cause"].mode()[0]
            
            # Predict
            pred = predict_incident(
                cause=top_cause,
                event_type="unplanned",
                corridor=cr["corridor"],
                hour=next_hour,
                dow=df["day_of_week"].mode()[0],
                veh_type="unknown"
            )
            
            risk_score = pred["closure_prob"]
            if risk_score > 0.15: # only show if closure risk > 15%
                radius = int(risk_score * 800)
                color = "#fc5c65" if risk_score > 0.3 else "#f7b731"
                folium.Circle(
                    [cr["lat"], cr["lon"]],
                    radius=radius,
                    popup=(
                        f"<b>🔮 Next-Hour Prediction: {cr['corridor']}</b><br>"
                        f"Hour: {next_hour:02d}:00<br>"
                        f"Top Cause: {top_cause.replace('_', ' ').title()}<br>"
                        f"Predicted Road Closure Risk: {risk_score:.1%}<br>"
                        f"Estimated Resolution: {pred['resolution_mins']:.0f} mins"
                    ),
                    color=color, fill=True, fill_opacity=0.4, weight=2,
                    tooltip=f"{cr['corridor']} (Risk: {risk_score:.0%})"
                ).add_to(m)

    if show_corridors:
        for _, cr in corridor_risk.head(12).iterrows():
            pts = df[df["corridor"] == cr["corridor"]][["latitude", "longitude"]].dropna()
            if len(pts) < 3:
                continue
            
            # Smart coordinate sorting based on aspect ratio
            lat_range = pts["latitude"].max() - pts["latitude"].min()
            lon_range = pts["longitude"].max() - pts["longitude"].min()
            if lon_range > lat_range:
                coords = pts.sample(min(40, len(pts)), random_state=42).sort_values("longitude").values.tolist()
            else:
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
    st.dataframe(df_filtered[available_cols].head(100), width="stretch", hide_index=True)

    st.markdown("---")
    st.markdown("### 🔗 Similar Incident Search")
    incident_id = st.selectbox("Select Incident ID", df_filtered["id"].head(200).tolist())

    if st.button("🔍 Find Similar Incidents", type="primary"):
        with st.spinner("🔍 Querying historical database for similar traffic patterns..."):
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

    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("chart_query"):
                chart = copilot_chart(msg["chart_query"])
                if chart:
                    st.plotly_chart(chart, width="stretch", key=f"hist_chart_{idx}")

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
                    st.plotly_chart(chart, width="stretch", key=f"new_chart_{len(st.session_state.messages)}")

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
            st.plotly_chart(fig, width="stretch")
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
            with st.spinner("🔮 Calculating proactive ML predictions..."):
                preds = predict_incident(pred_cause, pred_type, pred_corridor, pred_hour, pred_dow, pred_veh)
                severity = preds["severity"]
                closure_prob = preds["closure_prob"]
                median_res = preds["resolution_mins"]
                sev_conf = preds["severity_prob"]
                diversion_prob = max(closure_prob, preds["hist_closure"])
                resources = estimate_resources(pred_cause, severity.replace("HIGH", "High").replace("LOW", "Low"), diversion_prob)
                sev_class = "severity-high" if severity == "HIGH" else "severity-low"

            st.markdown("### 🎯 Prediction Results")

            gauge_col1, gauge_col2, gauge_col3 = st.columns(3)
            with gauge_col1:
                sev_color = "#fc5c65" if severity == "HIGH" else "#45aaf2"
                fig_sev = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=sev_conf * 100,
                    title={"text": f"Severity: {severity}", "font": {"size": 16, "color": "#e2e8f0"}},
                    number={"suffix": "%", "font": {"color": sev_color}},
                    gauge={
                        "axis": {"range": [0, 100], "tickcolor": "#4a5568"},
                        "bar": {"color": sev_color},
                        "bgcolor": "#1a1f2e",
                        "bordercolor": "#2d3748",
                        "steps": [
                            {"range": [0, 50], "color": "#252b3b"},
                            {"range": [50, 100], "color": "#1e2538"},
                        ],
                    },
                ))
                fig_sev.update_layout(height=220, paper_bgcolor="rgba(0,0,0,0)", font={"color": "#e2e8f0"}, margin=dict(t=60, b=10, l=20, r=20))
                st.plotly_chart(fig_sev, width="stretch")

            with gauge_col2:
                cl_color = "#fc5c65" if closure_prob > 0.3 else "#f7b731" if closure_prob > 0.1 else "#26de81"
                fig_cl = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=closure_prob * 100,
                    title={"text": "Road Closure Risk", "font": {"size": 16, "color": "#e2e8f0"}},
                    number={"suffix": "%", "font": {"color": cl_color}},
                    gauge={
                        "axis": {"range": [0, 100], "tickcolor": "#4a5568"},
                        "bar": {"color": cl_color},
                        "bgcolor": "#1a1f2e",
                        "bordercolor": "#2d3748",
                        "steps": [
                            {"range": [0, 30], "color": "#1a2e1a"},
                            {"range": [30, 70], "color": "#2e2a1a"},
                            {"range": [70, 100], "color": "#2e1a1a"},
                        ],
                    },
                ))
                fig_cl.update_layout(height=220, paper_bgcolor="rgba(0,0,0,0)", font={"color": "#e2e8f0"}, margin=dict(t=60, b=10, l=20, r=20))
                st.plotly_chart(fig_cl, width="stretch")

            with gauge_col3:
                st.markdown(f"""<div class="metric-card" style="margin-top:20px;">
                    <div class="metric-value">⏱️ {median_res:.0f}</div>
                    <div class="metric-label">Est. Resolution (min)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">👮 {resources['officers']}</div>
                    <div class="metric-label">Officers Needed</div>
                </div>""", unsafe_allow_html=True)
                if resources["tow_truck"]:
                    st.markdown('<div class="metric-card"><div class="metric-value">🚛</div><div class="metric-label">Tow Truck Needed</div></div>', unsafe_allow_html=True)
                if resources["ambulance"]:
                    st.markdown('<div class="metric-card"><div class="metric-value">🚑</div><div class="metric-label">Ambulance Alert</div></div>', unsafe_allow_html=True)

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

            st.markdown("### 📋 Resource Recommendation Grid")
            tow_truck_html = ""
            if resources["tow_truck"]:
                tow_truck_html = """
                <div style="flex: 1 1 180px; padding: 15px; background: linear-gradient(135deg, #3b1373 0%, #5c20ad 100%); border-radius: 8px; border: 1px solid #7e57c2; text-align: center; color: white;">
                    <div style="font-size: 2em; margin-bottom: 5px;">🚛</div>
                    <strong>Tow Truck</strong><br>
                    <span style="font-size:0.8em; opacity:0.8;">Required for vehicle clearance</span>
                </div>
                """
            
            ambulance_html = ""
            if resources["ambulance"]:
                ambulance_html = """
                <div style="flex: 1 1 180px; padding: 15px; background: linear-gradient(135deg, #781313 0%, #ad2020 100%); border-radius: 8px; border: 1px solid #e57373; text-align: center; color: white;">
                    <div style="font-size: 2em; margin-bottom: 5px;">🚑</div>
                    <strong>Ambulance Alert</strong><br>
                    <span style="font-size:0.8em; opacity:0.8;">Medical response team notified</span>
                </div>
                """

            st.markdown(f"""
            <div style="display:flex; flex-wrap:wrap; gap:10px; margin-top: 10px; margin-bottom: 20px;">
                <div style="flex: 1 1 180px; padding: 15px; background: linear-gradient(135deg, #132a73 0%, #2045ad 100%); border-radius: 8px; border: 1px solid #4a90e2; text-align: center; color: white;">
                    <div style="font-size: 2em; margin-bottom: 5px;">👮</div>
                    <strong>{resources['officers']} Officers</strong><br>
                    <span style="font-size:0.8em; opacity:0.8;">On-site traffic control & override</span>
                </div>
                <div style="flex: 1 1 180px; padding: 15px; background: linear-gradient(135deg, #734513 0%, #ad7020 100%); border-radius: 8px; border: 1px solid #f5a623; text-align: center; color: white;">
                    <div style="font-size: 2em; margin-bottom: 5px;">🚧</div>
                    <strong>{resources['barricades']} Barricades</strong><br>
                    <span style="font-size:0.8em; opacity:0.8;">Road closure & perimeter boundaries</span>
                </div>
                {tow_truck_html}
                {ambulance_html}
            </div>
            """, unsafe_allow_html=True)

            # Response Timeline
            dispatch_time = max(5, median_res * 0.15)
            arrival_time = max(10, median_res * 0.3)
            
            st.markdown(f"""
            <div style="margin-top:20px; margin-bottom:25px; padding: 20px; background:#1a1f2e; border: 1px solid #2d3748; border-radius:12px;">
                <h4 style="color:#e2e8f0; margin-top:0; margin-bottom: 15px;">⏱️ Predicted Response Timeline Milestones</h4>
                <div style="position:relative; padding-left: 20px; border-left: 2px solid #667eea; margin-left: 10px;">
                    <div style="margin-bottom: 15px; position:relative;">
                        <div style="position:absolute; left:-27px; top:3px; background:#667eea; border-radius:50%; width:12px; height:12px;"></div>
                        <strong style="color:#ffffff;">T + 0 min: Incident Detected</strong><br>
                        <span style="color:#a0aec0; font-size:0.85em;">Logged in Astram & NammaTraffic Command Platform</span>
                    </div>
                    <div style="margin-bottom: 15px; position:relative;">
                        <div style="position:absolute; left:-27px; top:3px; background:#667eea; border-radius:50%; width:12px; height:12px;"></div>
                        <strong style="color:#ffffff;">T + {dispatch_time:.0f} min: Dispatch Dispatch</strong><br>
                        <span style="color:#a0aec0; font-size:0.85em;">Dispatching {resources['officers']} officers & barricades</span>
                    </div>
                    <div style="margin-bottom: 15px; position:relative;">
                        <div style="position:absolute; left:-27px; top:3px; background:#667eea; border-radius:50%; width:12px; height:12px;"></div>
                        <strong style="color:#ffffff;">T + {arrival_time:.0f} min: Arrival & Setup</strong><br>
                        <span style="color:#a0aec0; font-size:0.85em;">Scene setup, perimeter safety bounds, and active diversions</span>
                    </div>
                    <div style="position:relative;">
                        <div style="position:absolute; left:-27px; top:3px; background:#26de81; border-radius:50%; width:12px; height:12px;"></div>
                        <strong style="color:#26de81;">T + {median_res:.0f} min: Predicted Clearance & Resolution</strong><br>
                        <span style="color:#a0aec0; font-size:0.85em;">Incident cleared from lane, normal flow restored</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("### 🔗 Similar Past Incidents")
            cause_data = df[df["event_cause"] == pred_cause]
            for _, row in cause_data.head(3).iterrows():
                res_str = f"{row['resolution_minutes']:.0f} min" if pd.notna(row.get("resolution_minutes")) else "N/A"
                st.markdown(f"- **{row['id']}** — {row['corridor']}, Resolution: {res_str}")


# ===================== PAGE: PROJECT DOCUMENTATION =====================
elif DATA_LOADED and page == "📑 Project Documentation":
    st.markdown("## 📑 Project Documentation")
    st.markdown("Technical depth for judges — architecture, ML results, data insights.")

    st.markdown("### 🏗️ System Architecture")
    st.markdown("""
    <div class="hero-card">
    <h4>NammaTraffic — End-to-End Architecture</h4>
    <pre style="color: #a0aec0; font-size: 0.85em;">
    ┌─────────────────────────────────────────────────────────────────┐
    │                    ASTRAM EVENT DATA (CSV)                      │
    │              8,173 incidents · 46 raw columns                    │
    └───────────────────────┬─────────────────────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │  DATA PIPELINE  │  → Cleaning, Feature Engineering
                    │ train_pipeline  │  → TF-IDF, Geo-Density, Temporal
                    └───────┬────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │  CatBoost    │ │  LightGBM   │ │  CatBoost    │
    │  Severity    │ │  Closure    │ │  Resolution  │
    │  F1=0.999    │ │  AUC=0.796  │ │  Regressor   │
    └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
           │                │                │
           └────────────────┼────────────────┘
                            │
                    ┌───────▼────────┐
                    │   STREAMLIT    │  ← 6-Page Command Center
                    │   app.py       │  ← Maps, Copilot, Predictor
                    └────────────────┘
    </pre>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🤖 ML Model Performance Summary")

    perf_data = []
    for model_name, md in model_perf.items():
        perf_data.append({
            "Model": model_name.replace('_', ' ').title(),
            "Algorithm": md['type'],
            "Target": md['target'],
            "Metric": md['metric'],
            "CV Mean": f"{md['cv_mean']}",
            "CV Std": f"±{md['cv_std']}",
        })
    st.dataframe(pd.DataFrame(perf_data), width="stretch", hide_index=True)

    st.markdown("---")
    st.markdown("### 📊 Dataset Statistics")

    stat_col1, stat_col2 = st.columns(2)
    with stat_col1:
        st.markdown(f"""
        | Statistic | Value |
        |---|---|
        | Total Incidents | **{len(df):,}** |
        | Time Range | Nov 2023 – Apr 2024 |
        | Corridors | **{df['corridor'].nunique()}** |
        | Zones | **{df['zone'].nunique() if 'zone' in df.columns else 'N/A'}** |
        | Police Stations | **{df['police_station'].nunique()}** |
        | Junctions | **{df['junction'].nunique() if 'junction' in df.columns else 'N/A'}** |
        """)
    with stat_col2:
        st.markdown(f"""
        | Statistic | Value |
        |---|---|
        | Unplanned Events | **{(df['event_type']=='unplanned').sum():,}** ({(df['event_type']=='unplanned').mean():.0%}) |
        | High Priority | **{df['priority_binary'].sum():,}** ({df['priority_binary'].mean():.0%}) |
        | Road Closures | **{df['requires_road_closure'].sum():,}** ({df['requires_road_closure'].mean():.0%}) |
        | Median Resolution | **{df['resolution_minutes'].median():.0f} min** |
        | Event Causes | **{df['event_cause'].nunique()}** types |
        | Resolution Data | **{df['resolution_minutes'].notna().sum():,}** ({df['resolution_minutes'].notna().mean():.0%}) |
        """)

    st.markdown("---")
    st.markdown("### 🔧 Feature Engineering Catalog")
    st.markdown("""
    | Feature | Type | Source | Description |
    |---|---|---|---|
    | `event_cause_grouped` | Categorical | Derived | Rare causes (< 50 incidents) grouped as `other_rare` |
    | `corridor_grouped` | Categorical | Derived | Rare corridors (< 30 incidents) grouped |
    | `veh_type_clean` | Categorical | Derived | Cleaned vehicle type with rare grouping |
    | `hour`, `day_of_week`, `month` | Numerical | Extracted | From `start_datetime` |
    | `is_weekend` | Binary | Derived | 1 if Saturday/Sunday |
    | `is_peak` | Binary | Derived | 1 if hour in [8-10, 17-19] |
    | `geo_density` | Numerical | Spatial | Count of incidents in same geo-bin (0.003° grid) |
    | `corridor_incident_count` | Numerical | Aggregated | Historical incident count per corridor |
    | `corridor_closure_rate` | Numerical | Aggregated | Historical road closure rate per corridor |
    | `corridor_high_priority_rate` | Numerical | Aggregated | Historical high-priority rate per corridor |
    | `hotspot_cluster` | Categorical | DBSCAN | Spatial cluster ID (-1 = noise) |
    | TF-IDF features | Numerical | NLP | Top-K terms from incident descriptions |
    """)

    st.markdown("---")
    st.markdown("### 📄 Reports & Documentation")
    st.markdown("24 comprehensive reports covering every aspect of the project:")

    report_categories = {
        "📋 Product & Strategy": ["product_definition.md", "theme_scoring.md", "demo_script.md", "final_submission_checklist.md"],
        "📊 Data Analysis": ["dataset_overview.md", "data_quality_report.md", "missing_values_report.md", "geography_report.md", "temporal_report.md"],
        "🏗️ Architecture": ["architecture_overview.md", "frontend_architecture.md", "backend_architecture.md", "database_schema.md", "api_design.md", "deployment_architecture.md", "gis_architecture.md"],
        "🤖 ML & AI": ["ml_architecture.md", "modeling_strategy.md", "target_definition.md", "feature_catalog.md", "ai_copilot_design.md"],
        "📅 Planning": ["24_hour_plan.md", "48_hour_plan.md", "final_judge_review.md"],
    }
    for category, files in report_categories.items():
        with st.expander(category):
            for f in files:
                st.markdown(f"- `reports/{f}`")


# ===================== FOOTER =====================
if DATA_LOADED:
    st.markdown("---")
    st.markdown(
        "<center><small>NammaTraffic v1.0 | Flipkart Gridlock Hackathon 2.0 | "
        "Event-Driven Congestion | Built for Bengaluru 🚦</small></center>",
        unsafe_allow_html=True,
    )
