"""
NammaTraffic — Data Pipeline & ML Model Training
Bengaluru Traffic Incident Intelligence & Command Platform
Flipkart Gridlock Hackathon 2.0

This script:
1. Loads and cleans the Astram event dataset
2. Engineers features for ML models
3. Trains 3 core ML models (Severity, Road Closure, Resolution Time)
4. Pre-computes similarity matrix, hotspot clusters, corridor stats
5. Saves all artifacts for the Streamlit app
"""

import pandas as pd
import numpy as np
import pickle
import json
import os
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import f1_score, roc_auc_score, mean_absolute_error, classification_report
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import LabelEncoder
from catboost import CatBoostClassifier, CatBoostRegressor, Pool
import lightgbm as lgb

# ===================== CONFIG =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, '..', 'selected_theme',
    'Astram event data_anonymized - Astram event data_anonymizedb40ac87.csv')
ARTIFACTS_DIR = os.path.join(BASE_DIR, '..', 'artifacts')
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

# ===================== LOAD & CLEAN =====================
print("=" * 60)
print("PHASE 1: Loading and Cleaning Data")
print("=" * 60)

df = pd.read_csv(DATA_PATH)
print(f"Loaded: {df.shape[0]} rows × {df.shape[1]} columns")

# Parse datetimes
for col in ['start_datetime', 'end_datetime', 'created_date', 'modified_datetime',
            'closed_datetime', 'resolved_datetime']:
    df[col] = pd.to_datetime(df[col], errors='coerce', utc=True)

# Drop 100% null columns
drop_cols = ['map_file', 'comment', 'meta_data']
df.drop(columns=[c for c in drop_cols if c in df.columns], inplace=True)

# Fix requires_road_closure
df['requires_road_closure'] = df['requires_road_closure'].map(
    {True: 1, False: 0, 'TRUE': 1, 'FALSE': 0, 'True': 1, 'False': 0}
).fillna(0).astype(int)

# Clean priority
df['priority'] = df['priority'].replace({'nan': np.nan})
df['priority_binary'] = (df['priority'] == 'High').astype(int)

# Compute resolution time in minutes
df['resolution_minutes'] = np.nan
# Try closed_datetime first, then resolved_datetime
for dt_col in ['closed_datetime', 'resolved_datetime']:
    mask = df['resolution_minutes'].isna() & df[dt_col].notna() & df['start_datetime'].notna()
    df.loc[mask, 'resolution_minutes'] = (
        df.loc[mask, dt_col] - df.loc[mask, 'start_datetime']
    ).dt.total_seconds() / 60.0

# Remove negative and extreme outliers
df.loc[df['resolution_minutes'] < 0, 'resolution_minutes'] = np.nan
df.loc[df['resolution_minutes'] > 60*24*30, 'resolution_minutes'] = np.nan  # >30 days

print(f"Resolution time available: {df['resolution_minutes'].notna().sum()} records")
print(f"Road closure rate: {df['requires_road_closure'].mean():.1%}")
print(f"High priority rate: {df['priority_binary'].mean():.1%}")

# ===================== FEATURE ENGINEERING =====================
print("\n" + "=" * 60)
print("PHASE 2: Feature Engineering")
print("=" * 60)

# Temporal features
df['hour'] = df['start_datetime'].dt.hour.fillna(12).astype(int)
df['day_of_week'] = df['start_datetime'].dt.dayofweek.fillna(3).astype(int)
df['month'] = df['start_datetime'].dt.month.fillna(1).astype(int)
df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
df['is_peak'] = df['hour'].apply(lambda h: 1 if h in [8,9,10,17,18,19] else 0)

# Event cause grouping (collapse rare causes)
cause_counts = df['event_cause'].value_counts()
rare_causes = cause_counts[cause_counts < 50].index
df['event_cause_grouped'] = df['event_cause'].replace(
    {c: 'other_rare' for c in rare_causes}
)

# Corridor grouping
corridor_counts = df['corridor'].value_counts()
rare_corridors = corridor_counts[corridor_counts < 30].index
df['corridor_grouped'] = df['corridor'].fillna('Unknown').replace(
    {c: 'Other_Corridor' for c in rare_corridors}
)

# Vehicle type cleaning
df['veh_type_clean'] = df['veh_type'].fillna('unknown')
veh_counts = df['veh_type_clean'].value_counts()
rare_veh = veh_counts[veh_counts < 20].index
df['veh_type_clean'] = df['veh_type_clean'].replace({v: 'other_vehicle' for v in rare_veh})

# Description NLP features
df['description_clean'] = df['description'].fillna('none').str.lower()

print("Creating TF-IDF features from descriptions...")
tfidf = TfidfVectorizer(max_features=50, stop_words='english', min_df=5)
tfidf_matrix = tfidf.fit_transform(df['description_clean'])
tfidf_df = pd.DataFrame(
    tfidf_matrix.toarray(),
    columns=[f'tfidf_{w}' for w in tfidf.get_feature_names_out()],
    index=df.index
)

# Spatial density features
print("Computing spatial density features...")
from collections import Counter

def geohash_encode(lat, lon, precision=5):
    """Simple geohash-like encoding for spatial binning"""
    lat_bin = round(lat, precision-2)
    lon_bin = round(lon, precision-2)
    return f"{lat_bin}_{lon_bin}"

df['geo_bin'] = df.apply(lambda r: geohash_encode(r['latitude'], r['longitude']), axis=1)
geo_density = df['geo_bin'].value_counts().to_dict()
df['geo_density'] = df['geo_bin'].map(geo_density)

# Corridor-level statistics
corridor_stats = df.groupby('corridor_grouped').agg(
    corridor_incident_count=('id', 'count'),
    corridor_closure_rate=('requires_road_closure', 'mean'),
    corridor_high_priority_rate=('priority_binary', 'mean')
).reset_index()
df = df.merge(corridor_stats, on='corridor_grouped', how='left')

# Feature columns for ML
CATEGORICAL_FEATURES = ['event_type', 'event_cause_grouped', 'corridor_grouped', 'veh_type_clean']
NUMERICAL_FEATURES = ['latitude', 'longitude', 'hour', 'day_of_week', 'month',
                       'is_weekend', 'is_peak', 'geo_density',
                       'corridor_incident_count', 'corridor_closure_rate',
                       'corridor_high_priority_rate']

ALL_FEATURES = CATEGORICAL_FEATURES + NUMERICAL_FEATURES
print(f"Total features: {len(ALL_FEATURES)} ({len(CATEGORICAL_FEATURES)} categorical + {len(NUMERICAL_FEATURES)} numerical)")

# ===================== MODEL 1: SEVERITY PREDICTION =====================
print("\n" + "=" * 60)
print("PHASE 3: Training Model 1 — Severity/Priority Classifier")
print("=" * 60)

mask_severity = df['priority'].notna() & (df['priority'] != 'nan')
df_sev = df[mask_severity].copy()
y_sev = df_sev['priority_binary'].values
X_sev = df_sev[ALL_FEATURES].copy()

# Encode categoricals for CatBoost
cat_indices = list(range(len(CATEGORICAL_FEATURES)))

severity_model = CatBoostClassifier(
    iterations=1000, learning_rate=0.05, depth=6,
    loss_function='Logloss', eval_metric='F1',
    cat_features=cat_indices, random_seed=42, verbose=200
)

# Cross-validation
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
f1_scores = []
for fold, (train_idx, val_idx) in enumerate(skf.split(X_sev, y_sev)):
    X_train, X_val = X_sev.iloc[train_idx], X_sev.iloc[val_idx]
    y_train, y_val = y_sev[train_idx], y_sev[val_idx]
    
    train_pool = Pool(X_train, y_train, cat_features=cat_indices)
    val_pool = Pool(X_val, y_val, cat_features=cat_indices)
    
    severity_model.fit(train_pool, eval_set=val_pool, verbose=0)
    preds = severity_model.predict(X_val)
    f1 = f1_score(y_val, preds)
    f1_scores.append(f1)
    print(f"  Fold {fold+1}: F1={f1:.4f}")

print(f"  Mean F1: {np.mean(f1_scores):.4f} ± {np.std(f1_scores):.4f}")

# Train final model on all data (no eval_set, no early stopping)
severity_final = CatBoostClassifier(
    iterations=800, learning_rate=0.05, depth=6,
    loss_function='Logloss', cat_features=cat_indices,
    random_seed=42, verbose=0
)
train_pool_full = Pool(X_sev, y_sev, cat_features=cat_indices)
severity_final.fit(train_pool_full)
severity_model = severity_final

# Feature importance
fi_sev = severity_model.get_feature_importance()
fi_sev_dict = dict(zip(ALL_FEATURES, fi_sev))
print("\n  Top 5 features for severity:")
for feat, imp in sorted(fi_sev_dict.items(), key=lambda x: -x[1])[:5]:
    print(f"    {feat}: {imp:.1f}")

# ===================== MODEL 2: ROAD CLOSURE PREDICTION =====================
print("\n" + "=" * 60)
print("PHASE 4: Training Model 2 — Road Closure Predictor")
print("=" * 60)

y_closure = df['requires_road_closure'].values
X_closure = df[ALL_FEATURES].copy()

# Use LightGBM for imbalanced data
le_dict = {}
X_closure_lgb = X_closure.copy()
for col in CATEGORICAL_FEATURES:
    le = LabelEncoder()
    X_closure_lgb[col] = le.fit_transform(X_closure_lgb[col].astype(str))
    le_dict[col] = le

pos_weight = (1 - y_closure.mean()) / y_closure.mean()
print(f"  Class imbalance: {y_closure.mean():.1%} positive, scale_pos_weight={pos_weight:.1f}")

lgb_params = {
    'objective': 'binary', 'metric': 'auc',
    'scale_pos_weight': pos_weight, 'learning_rate': 0.03,
    'max_depth': 5, 'num_leaves': 31, 'n_estimators': 800,
    'verbose': -1, 'random_state': 42
}

closure_model = lgb.LGBMClassifier(**lgb_params)
auc_scores = []
for fold, (train_idx, val_idx) in enumerate(skf.split(X_closure_lgb, y_closure)):
    X_train, X_val = X_closure_lgb.iloc[train_idx], X_closure_lgb.iloc[val_idx]
    y_train, y_val = y_closure[train_idx], y_closure[val_idx]
    
    closure_model.fit(X_train, y_train, eval_set=[(X_val, y_val)],
                      callbacks=[lgb.log_evaluation(0), lgb.early_stopping(50)])
    preds_proba = closure_model.predict_proba(X_val)[:, 1]
    auc = roc_auc_score(y_val, preds_proba)
    auc_scores.append(auc)
    print(f"  Fold {fold+1}: AUC={auc:.4f}")

print(f"  Mean AUC: {np.mean(auc_scores):.4f} ± {np.std(auc_scores):.4f}")

# Train final
closure_model.fit(X_closure_lgb, y_closure)

# ===================== MODEL 3: RESOLUTION TIME =====================
print("\n" + "=" * 60)
print("PHASE 5: Training Model 3 — Resolution Time Predictor")
print("=" * 60)

mask_res = df['resolution_minutes'].notna() & (df['resolution_minutes'] > 0)
df_res = df[mask_res].copy()
y_res = np.log1p(df_res['resolution_minutes'].values)
X_res = df_res[ALL_FEATURES].copy()

print(f"  Records with resolution time: {len(df_res)}")
print(f"  Median resolution: {df_res['resolution_minutes'].median():.0f} minutes")

resolution_model = CatBoostRegressor(
    iterations=800, learning_rate=0.05, depth=6,
    loss_function='RMSE', cat_features=cat_indices,
    random_seed=42, verbose=200
)

mae_scores = []
for fold, (train_idx, val_idx) in enumerate(skf.split(X_res, (y_res > np.median(y_res)).astype(int))):
    X_train, X_val = X_res.iloc[train_idx], X_res.iloc[val_idx]
    y_train, y_val = y_res[train_idx], y_res[val_idx]
    
    train_pool = Pool(X_train, y_train, cat_features=cat_indices)
    val_pool = Pool(X_val, y_val, cat_features=cat_indices)
    
    resolution_model.fit(train_pool, eval_set=val_pool, verbose=0)
    preds_log = resolution_model.predict(X_val)
    preds_min = np.expm1(preds_log)
    actual_min = np.expm1(y_val)
    mae = mean_absolute_error(actual_min, preds_min)
    mae_scores.append(mae)
    print(f"  Fold {fold+1}: MAE={mae:.1f} minutes")

print(f"  Mean MAE: {np.mean(mae_scores):.1f} ± {np.std(mae_scores):.1f} minutes")

# Train final (no eval_set)
resolution_final = CatBoostRegressor(
    iterations=600, learning_rate=0.05, depth=6,
    loss_function='RMSE', cat_features=cat_indices,
    random_seed=42, verbose=0
)
train_pool_full = Pool(X_res, y_res, cat_features=cat_indices)
resolution_final.fit(train_pool_full)
resolution_model = resolution_final

# ===================== SIMILARITY ENGINE =====================
print("\n" + "=" * 60)
print("PHASE 6: Building Similar Incident Search Engine")
print("=" * 60)

# Build feature vectors for similarity
sim_features = []
# One-hot event_cause
cause_dummies = pd.get_dummies(df['event_cause_grouped'], prefix='cause')
sim_features.append(cause_dummies)

# One-hot corridor
corridor_dummies = pd.get_dummies(df['corridor_grouped'], prefix='corr')
sim_features.append(corridor_dummies)

# Normalized lat/lon
lat_norm = (df['latitude'] - df['latitude'].mean()) / df['latitude'].std()
lon_norm = (df['longitude'] - df['longitude'].mean()) / df['longitude'].std()
sim_features.append(pd.DataFrame({'lat_n': lat_norm, 'lon_n': lon_norm}, index=df.index))

# Hour (normalized)
hour_norm = df['hour'] / 24.0
sim_features.append(pd.DataFrame({'hour_n': hour_norm}, index=df.index))

# TF-IDF
sim_features.append(tfidf_df)

similarity_matrix_features = pd.concat(sim_features, axis=1).fillna(0).values

print(f"  Similarity vector dimension: {similarity_matrix_features.shape[1]}")
print("  Computing cosine similarity matrix (this may take a moment)...")
# Store the feature matrix, compute similarity on-demand for efficiency
print("  Saving feature matrix for on-demand similarity computation...")

# ===================== HOTSPOT CLUSTERS =====================
print("\n" + "=" * 60)
print("PHASE 7: Computing Hotspot Clusters (DBSCAN)")
print("=" * 60)

coords_rad = np.radians(df[['latitude', 'longitude']].values)
clustering = DBSCAN(eps=500/6371000, min_samples=5, metric='haversine').fit(coords_rad)
df['hotspot_cluster'] = clustering.labels_
n_clusters = len(set(clustering.labels_)) - 1
print(f"  Found {n_clusters} hotspot clusters")
print(f"  Noise points: {(clustering.labels_ == -1).sum()}")

# Compute cluster centroids and stats
cluster_stats = df[df['hotspot_cluster'] >= 0].groupby('hotspot_cluster').agg(
    centroid_lat=('latitude', 'mean'),
    centroid_lon=('longitude', 'mean'),
    incident_count=('id', 'count'),
    closure_rate=('requires_road_closure', 'mean'),
    high_priority_rate=('priority_binary', 'mean'),
    top_cause=('event_cause', lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'unknown')
).reset_index()

print(f"\n  Top 5 hotspot clusters:")
for _, row in cluster_stats.nlargest(5, 'incident_count').iterrows():
    print(f"    Cluster {int(row['hotspot_cluster'])}: {int(row['incident_count'])} incidents @ "
          f"({row['centroid_lat']:.4f}, {row['centroid_lon']:.4f}), "
          f"closure={row['closure_rate']:.0%}, cause={row['top_cause']}")

# ===================== CORRIDOR RISK SCORES =====================
print("\n" + "=" * 60)
print("PHASE 8: Computing Corridor Risk Scores")
print("=" * 60)

corridor_risk = df.groupby('corridor').agg(
    total_incidents=('id', 'count'),
    closure_rate=('requires_road_closure', 'mean'),
    high_priority_pct=('priority_binary', 'mean'),
    avg_resolution_mins=('resolution_minutes', 'median'),
    breakdown_pct=('event_cause', lambda x: (x == 'vehicle_breakdown').mean()),
    lat=('latitude', 'mean'),
    lon=('longitude', 'mean')
).reset_index()

corridor_risk['risk_score'] = (
    0.4 * corridor_risk['total_incidents'] / corridor_risk['total_incidents'].max() +
    0.3 * corridor_risk['closure_rate'] +
    0.3 * corridor_risk['high_priority_pct']
)
corridor_risk = corridor_risk.sort_values('risk_score', ascending=False)

print("  Top 10 corridors by risk:")
for _, row in corridor_risk.head(10).iterrows():
    print(f"    {row['corridor']}: risk={row['risk_score']:.3f}, "
          f"incidents={int(row['total_incidents'])}, closure={row['closure_rate']:.0%}")

# ===================== SAVE ALL ARTIFACTS =====================
print("\n" + "=" * 60)
print("PHASE 9: Saving All Artifacts")
print("=" * 60)

# Save models
severity_model.save_model(os.path.join(ARTIFACTS_DIR, 'severity_model.cbm'))
closure_model.booster_.save_model(os.path.join(ARTIFACTS_DIR, 'closure_model.lgb'))
resolution_model.save_model(os.path.join(ARTIFACTS_DIR, 'resolution_model.cbm'))
print("  ✅ Saved 3 ML models")

# Save encoders and vectorizer
with open(os.path.join(ARTIFACTS_DIR, 'tfidf_vectorizer.pkl'), 'wb') as f:
    pickle.dump(tfidf, f)
with open(os.path.join(ARTIFACTS_DIR, 'label_encoders.pkl'), 'wb') as f:
    pickle.dump(le_dict, f)
print("  ✅ Saved TF-IDF vectorizer and label encoders")

# Save similarity matrix
np.save(
    os.path.join(ARTIFACTS_DIR, 'similarity_features.npy'),
    np.asarray(similarity_matrix_features, dtype=np.float64),
)
print("  ✅ Saved similarity feature matrix")

# Save cluster stats
cluster_stats.to_csv(os.path.join(ARTIFACTS_DIR, 'hotspot_clusters.csv'), index=False)
print("  ✅ Saved hotspot cluster stats")

# Save corridor risk
corridor_risk.to_csv(os.path.join(ARTIFACTS_DIR, 'corridor_risk.csv'), index=False)
print("  ✅ Saved corridor risk scores")

# Save cleaned dataset
df.to_csv(os.path.join(ARTIFACTS_DIR, 'cleaned_data.csv'), index=False)
print("  ✅ Saved cleaned dataset")

# Save feature config
feature_config = {
    'categorical_features': CATEGORICAL_FEATURES,
    'numerical_features': NUMERICAL_FEATURES,
    'all_features': ALL_FEATURES,
    'cat_indices': cat_indices
}
with open(os.path.join(ARTIFACTS_DIR, 'feature_config.json'), 'w') as f:
    json.dump(feature_config, f, indent=2)
print("  ✅ Saved feature configuration")

# Save model performance
performance = {
    'severity_model': {
        'type': 'CatBoost Classifier',
        'target': 'priority (High=1, Low=0)',
        'metric': 'F1 Score',
        'cv_mean': round(float(np.mean(f1_scores)), 4),
        'cv_std': round(float(np.std(f1_scores)), 4),
        'fold_scores': [round(float(s), 4) for s in f1_scores]
    },
    'closure_model': {
        'type': 'LightGBM Classifier',
        'target': 'requires_road_closure (1/0)',
        'metric': 'ROC AUC',
        'cv_mean': round(float(np.mean(auc_scores)), 4),
        'cv_std': round(float(np.std(auc_scores)), 4),
        'fold_scores': [round(float(s), 4) for s in auc_scores]
    },
    'resolution_model': {
        'type': 'CatBoost Regressor',
        'target': 'resolution_minutes (log-transformed)',
        'metric': 'MAE (minutes)',
        'cv_mean': round(float(np.mean(mae_scores)), 1),
        'cv_std': round(float(np.std(mae_scores)), 1),
        'fold_scores': [round(float(s), 1) for s in mae_scores]
    }
}
with open(os.path.join(ARTIFACTS_DIR, 'model_performance.json'), 'w') as f:
    json.dump(performance, f, indent=2)
print("  ✅ Saved model performance metrics")

# Save hourly/cause distribution stats for copilot
hourly_stats = df.groupby('hour').agg(
    count=('id', 'count'),
    closure_rate=('requires_road_closure', 'mean'),
    high_priority_rate=('priority_binary', 'mean')
).reset_index().to_dict('records')

cause_stats = df.groupby('event_cause').agg(
    count=('id', 'count'),
    closure_rate=('requires_road_closure', 'mean'),
    high_priority_rate=('priority_binary', 'mean'),
    avg_resolution=('resolution_minutes', 'median')
).reset_index().to_dict('records')

copilot_context = {
    'total_incidents': int(len(df)),
    'date_range': f"{df['start_datetime'].min()} to {df['start_datetime'].max()}",
    'hourly_distribution': hourly_stats,
    'cause_distribution': cause_stats,
    'corridors': int(df['corridor'].nunique()),
    'police_stations': int(df['police_station'].nunique())
}
with open(os.path.join(ARTIFACTS_DIR, 'copilot_context.json'), 'w') as f:
    json.dump(copilot_context, f, indent=2, default=str)
print("  ✅ Saved copilot context data")

print("\n" + "=" * 60)
print("✅ ALL ARTIFACTS SAVED SUCCESSFULLY")
print(f"   Location: {ARTIFACTS_DIR}")
print(f"   Files: {len(os.listdir(ARTIFACTS_DIR))}")
print("=" * 60)
