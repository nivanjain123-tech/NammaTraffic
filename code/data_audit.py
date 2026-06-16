#!/usr/bin/env python3
"""
Comprehensive Data Audit for Astram Event Dataset
Produces 7 markdown reports for Flipkart Gridlock Hackathon 2.0
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# ─── PATHS ───
DATA_PATH = Path("/Users/nivanvishaljain/Desktop/Hackerearth/Gridlock_Round2/selected_theme/Astram event data_anonymized - Astram event data_anonymizedb40ac87.csv")
REPORT_DIR = Path("/Users/nivanvishaljain/Desktop/Hackerearth/Gridlock_Round2/reports")
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# ─── LOAD DATA ───
print("Loading dataset...")
df = pd.read_csv(DATA_PATH, low_memory=False)
print(f"Loaded {len(df)} rows x {len(df.columns)} columns")

# Replace 'NULL' strings with NaN
df.replace('NULL', np.nan, inplace=True)
df.replace('null', np.nan, inplace=True)

# ─── Parse datetime columns ───
datetime_cols = ['start_datetime', 'end_datetime', 'modified_datetime', 'created_date', 
                 'closed_datetime', 'resolved_datetime']
for col in datetime_cols:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

# ========================================================================
# REPORT 1: DATASET OVERVIEW
# ========================================================================
print("\n=== Generating Report 1: Dataset Overview ===")

report1 = []
report1.append("# 📊 Dataset Overview Report\n")
report1.append("## Astram Event Data — Bengaluru Traffic Incidents\n")
report1.append(f"**File**: `{DATA_PATH.name}`\n")
report1.append(f"**Rows**: {len(df):,}")
report1.append(f"**Columns**: {len(df.columns)}")
report1.append(f"**Memory Usage**: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB\n")

report1.append("## Column Schema\n")
report1.append("| # | Column Name | Dtype | Non-Null Count | Null Count | Null % | Sample Value |")
report1.append("|---|------------|-------|---------------|-----------|--------|-------------|")
for i, col in enumerate(df.columns, 1):
    non_null = df[col].notna().sum()
    null_count = df[col].isna().sum()
    null_pct = null_count / len(df) * 100
    dtype = str(df[col].dtype)
    sample = str(df[col].dropna().iloc[0])[:60] if non_null > 0 else "N/A"
    sample = sample.replace("|", "\\|")
    report1.append(f"| {i} | `{col}` | {dtype} | {non_null:,} | {null_count:,} | {null_pct:.1f}% | {sample} |")

report1.append("\n## Data Types Summary\n")
dtype_counts = df.dtypes.astype(str).value_counts()
for dtype, count in dtype_counts.items():
    report1.append(f"- **{dtype}**: {count} columns")

report1.append("\n## First 5 Row IDs\n")
report1.append("```")
for _, row in df.head(5).iterrows():
    report1.append(f"ID: {row['id']}, Type: {row.get('event_type', 'N/A')}, Status: {row.get('status', 'N/A')}, Cause: {row.get('event_cause', 'N/A')}")
report1.append("```\n")

# Key column value counts preview
report1.append("## Key Column Distributions (Preview)\n")
key_cats = ['event_type', 'status', 'event_cause', 'priority', 'requires_road_closure', 'authenticated']
for col in key_cats:
    if col in df.columns:
        vc = df[col].value_counts(dropna=False).head(10)
        report1.append(f"### `{col}` (top values)\n")
        report1.append("| Value | Count | % |")
        report1.append("|-------|-------|---|")
        for val, cnt in vc.items():
            pct = cnt / len(df) * 100
            report1.append(f"| {val} | {cnt:,} | {pct:.1f}% |")
        report1.append("")

(REPORT_DIR / "dataset_overview.md").write_text("\n".join(report1))
print("  ✅ dataset_overview.md written")

# ========================================================================
# REPORT 2: MISSING VALUES REPORT
# ========================================================================
print("\n=== Generating Report 2: Missing Values Report ===")

report2 = []
report2.append("# 🕳️ Missing Values Report\n")
report2.append(f"**Total Records**: {len(df):,}\n")

# Summary
total_cells = len(df) * len(df.columns)
missing_cells = df.isna().sum().sum()
report2.append(f"**Total Cells**: {total_cells:,}")
report2.append(f"**Missing Cells**: {int(missing_cells):,}")
report2.append(f"**Overall Missing Rate**: {missing_cells/total_cells*100:.2f}%\n")

# Per column
report2.append("## Missing Values by Column\n")
report2.append("| Column | Non-Null | Missing | Missing % | Severity |")
report2.append("|--------|---------|---------|-----------|----------|")

missing_df = pd.DataFrame({
    'column': df.columns,
    'non_null': df.notna().sum().values,
    'missing': df.isna().sum().values,
    'missing_pct': (df.isna().sum().values / len(df) * 100)
}).sort_values('missing_pct', ascending=False)

for _, row in missing_df.iterrows():
    severity = "🟢 Good" if row['missing_pct'] < 5 else ("🟡 Moderate" if row['missing_pct'] < 50 else "🔴 Critical")
    report2.append(f"| `{row['column']}` | {int(row['non_null']):,} | {int(row['missing']):,} | {row['missing_pct']:.1f}% | {severity} |")

# Categorize
report2.append("\n## Missing Value Categories\n")

complete_cols = missing_df[missing_df['missing_pct'] == 0]['column'].tolist()
low_missing = missing_df[(missing_df['missing_pct'] > 0) & (missing_df['missing_pct'] < 5)]['column'].tolist()
moderate_missing = missing_df[(missing_df['missing_pct'] >= 5) & (missing_df['missing_pct'] < 50)]['column'].tolist()
high_missing = missing_df[missing_df['missing_pct'] >= 50]['column'].tolist()

report2.append(f"### 🟢 Complete Columns (0% missing): {len(complete_cols)}")
report2.append(f"```\n{', '.join(complete_cols)}\n```\n")

report2.append(f"### 🟡 Low Missing (<5%): {len(low_missing)}")
report2.append(f"```\n{', '.join(low_missing)}\n```\n")

report2.append(f"### 🟠 Moderate Missing (5-50%): {len(moderate_missing)}")
report2.append(f"```\n{', '.join(moderate_missing)}\n```\n")

report2.append(f"### 🔴 High Missing (>50%): {len(high_missing)}")
report2.append(f"```\n{', '.join(high_missing)}\n```\n")

# Rows with most missing
row_missing = df.isna().sum(axis=1)
report2.append("## Row-Level Missing Analysis\n")
report2.append(f"- **Max missing columns per row**: {row_missing.max()}")
report2.append(f"- **Mean missing columns per row**: {row_missing.mean():.1f}")
report2.append(f"- **Median missing columns per row**: {row_missing.median():.0f}")
report2.append(f"- **Rows with 0 missing**: {(row_missing == 0).sum():,}")
report2.append(f"- **Rows with >10 missing**: {(row_missing > 10).sum():,}")
report2.append(f"- **Rows with >20 missing**: {(row_missing > 20).sum():,}\n")

# Correlation of missingness
report2.append("## Missing Together Analysis\n")
report2.append("Columns that tend to be missing together (potential structural patterns):\n")

# Check some groups
groups = {
    "End location group": ['endlatitude', 'endlongitude', 'end_address'],
    "Vehicle group": ['veh_type', 'veh_no'],
    "Resolution group": ['resolved_at_address', 'resolved_at_latitude', 'resolved_at_longitude', 'resolved_datetime'],
    "Closure group": ['closed_datetime', 'closed_by_id'],
    "Geo admin group": ['zone', 'junction', 'gba_identifier'],
    "Breakdown-specific": ['cargo_material', 'reason_breakdown', 'age_of_truck'],
}

for name, cols in groups.items():
    existing_cols = [c for c in cols if c in df.columns]
    if existing_cols:
        all_missing = df[existing_cols].isna().all(axis=1).sum()
        any_missing = df[existing_cols].isna().any(axis=1).sum()
        report2.append(f"- **{name}** ({', '.join(existing_cols)}): all-missing={all_missing:,} rows, any-missing={any_missing:,} rows")

(REPORT_DIR / "missing_values_report.md").write_text("\n".join(report2))
print("  ✅ missing_values_report.md written")

# ========================================================================
# REPORT 3: FEATURE CATALOG
# ========================================================================
print("\n=== Generating Report 3: Feature Catalog ===")

report3 = []
report3.append("# 📋 Feature Catalog\n")
report3.append("Each column categorized with type, unique values, and distribution.\n")

# Classify columns
categorical_cols = ['event_type', 'event_cause', 'requires_road_closure', 'status', 'authenticated',
                    'direction', 'veh_type', 'corridor', 'priority', 'cargo_material', 'reason_breakdown',
                    'police_station', 'zone', 'junction', 'gba_identifier', 'map_file']
numerical_cols = ['latitude', 'longitude', 'endlatitude', 'endlongitude', 
                  'resolved_at_latitude', 'resolved_at_longitude', 'age_of_truck']
temporal_cols = ['start_datetime', 'end_datetime', 'modified_datetime', 'created_date',
                 'closed_datetime', 'resolved_datetime']
text_cols = ['address', 'end_address', 'description', 'comment', 'resolved_at_address', 'route_path', 'meta_data']
id_cols = ['id', 'veh_no', 'client_id', 'created_by_id', 'last_modified_by_id', 
           'assigned_to_police_id', 'citizen_accident_id', 'closed_by_id', 'resolved_by_id', 'kgid']

# Summary table
report3.append("## Feature Classification Summary\n")
report3.append("| Category | Count | Columns |")
report3.append("|----------|-------|---------|")
cat_existing = [c for c in categorical_cols if c in df.columns]
num_existing = [c for c in numerical_cols if c in df.columns]
temp_existing = [c for c in temporal_cols if c in df.columns]
text_existing = [c for c in text_cols if c in df.columns]
id_existing = [c for c in id_cols if c in df.columns]
report3.append(f"| Categorical | {len(cat_existing)} | {', '.join(cat_existing)} |")
report3.append(f"| Numerical | {len(num_existing)} | {', '.join(num_existing)} |")
report3.append(f"| Temporal | {len(temp_existing)} | {', '.join(temp_existing)} |")
report3.append(f"| Text/Free-form | {len(text_existing)} | {', '.join(text_existing)} |")
report3.append(f"| Identifier | {len(id_existing)} | {', '.join(id_existing)} |")

# Detailed per-feature
report3.append("\n---\n## Detailed Feature Analysis\n")

# Categorical features
report3.append("### 🏷️ Categorical Features\n")
for col in cat_existing:
    nunique = df[col].nunique()
    non_null = df[col].notna().sum()
    report3.append(f"#### `{col}`")
    report3.append(f"- **Unique values**: {nunique}")
    report3.append(f"- **Non-null**: {non_null:,} ({non_null/len(df)*100:.1f}%)")
    report3.append(f"- **Top values**:\n")
    vc = df[col].value_counts(dropna=False).head(15)
    report3.append("| Value | Count | % |")
    report3.append("|-------|-------|---|")
    for val, cnt in vc.items():
        pct = cnt / len(df) * 100
        val_str = str(val)[:50]
        report3.append(f"| {val_str} | {cnt:,} | {pct:.1f}% |")
    report3.append("")

# Numerical features
report3.append("### 🔢 Numerical Features\n")
for col in num_existing:
    report3.append(f"#### `{col}`")
    non_null = df[col].notna().sum()
    report3.append(f"- **Non-null**: {non_null:,} ({non_null/len(df)*100:.1f}%)")
    if non_null > 0:
        desc = df[col].describe()
        report3.append(f"- **Min**: {desc.get('min', 'N/A')}")
        report3.append(f"- **Max**: {desc.get('max', 'N/A')}")
        report3.append(f"- **Mean**: {desc.get('mean', 'N/A'):.6f}" if pd.notna(desc.get('mean')) else f"- **Mean**: N/A")
        report3.append(f"- **Std**: {desc.get('std', 'N/A'):.6f}" if pd.notna(desc.get('std')) else f"- **Std**: N/A")
        report3.append(f"- **Median**: {desc.get('50%', 'N/A')}")
    
    # For lat/lon check zeros
    if col in ['endlatitude', 'endlongitude']:
        zeros = (df[col] == 0).sum()
        report3.append(f"- **⚠️ Zero values**: {zeros:,} (likely placeholders)")
    report3.append("")

# Temporal features
report3.append("### 📅 Temporal Features\n")
for col in temp_existing:
    report3.append(f"#### `{col}`")
    non_null = df[col].notna().sum()
    report3.append(f"- **Non-null**: {non_null:,} ({non_null/len(df)*100:.1f}%)")
    if non_null > 0:
        report3.append(f"- **Min**: {df[col].min()}")
        report3.append(f"- **Max**: {df[col].max()}")
        report3.append(f"- **Range**: {df[col].max() - df[col].min()}")
    report3.append("")

# Text features
report3.append("### 📝 Text Features\n")
for col in text_existing:
    report3.append(f"#### `{col}`")
    non_null = df[col].notna().sum()
    report3.append(f"- **Non-null**: {non_null:,} ({non_null/len(df)*100:.1f}%)")
    if non_null > 0:
        lengths = df[col].dropna().str.len()
        report3.append(f"- **Avg length**: {lengths.mean():.0f} chars")
        report3.append(f"- **Max length**: {lengths.max():.0f} chars")
        report3.append(f"- **Min length**: {lengths.min():.0f} chars")
        nunique = df[col].nunique()
        report3.append(f"- **Unique values**: {nunique:,}")
    report3.append("")

# ID features
report3.append("### 🔑 Identifier Features\n")
for col in id_existing:
    report3.append(f"#### `{col}`")
    non_null = df[col].notna().sum()
    nunique = df[col].nunique()
    report3.append(f"- **Non-null**: {non_null:,} ({non_null/len(df)*100:.1f}%)")
    report3.append(f"- **Unique values**: {nunique:,}")
    if nunique <= 20 and non_null > 0:
        vc = df[col].value_counts().head(10)
        report3.append(f"- **Top values**:")
        for val, cnt in vc.items():
            report3.append(f"  - `{val}`: {cnt}")
    report3.append("")

(REPORT_DIR / "feature_catalog.md").write_text("\n".join(report3))
print("  ✅ feature_catalog.md written")

# ========================================================================
# REPORT 4: GEOGRAPHY REPORT
# ========================================================================
print("\n=== Generating Report 4: Geography Report ===")

report4 = []
report4.append("# 🗺️ Geography Report\n")

# Lat/Long bounds
valid_lat = df['latitude'][(df['latitude'] > 10) & (df['latitude'] < 15)]
valid_lon = df['longitude'][(df['longitude'] > 75) & (df['longitude'] < 80)]

report4.append("## Coordinate Bounds\n")
report4.append("### Primary Location (latitude, longitude)\n")
report4.append(f"- **Records with coordinates**: {df['latitude'].notna().sum():,}")
report4.append(f"- **Lat range**: {valid_lat.min():.6f} to {valid_lat.max():.6f}")
report4.append(f"- **Lon range**: {valid_lon.min():.6f} to {valid_lon.max():.6f}")
report4.append(f"- **Lat mean**: {valid_lat.mean():.6f}")
report4.append(f"- **Lon mean**: {valid_lon.mean():.6f}")
report4.append(f"- **Lat std**: {valid_lat.std():.6f}")
report4.append(f"- **Lon std**: {valid_lon.std():.6f}")

# Centroid
report4.append(f"\n**Centroid**: ({valid_lat.mean():.4f}, {valid_lon.mean():.4f}) — Bengaluru core area\n")

# Bounding box
report4.append("### Bounding Box (for valid Bengaluru coordinates)\n")
report4.append(f"- **SW corner**: ({valid_lat.min():.4f}, {valid_lon.min():.4f})")
report4.append(f"- **NE corner**: ({valid_lat.max():.4f}, {valid_lon.max():.4f})")

# End coordinates
report4.append("\n### End Location (endlatitude, endlongitude)\n")
valid_endlat = df['endlatitude'][(df['endlatitude'] > 10) & (df['endlatitude'] < 15)]
valid_endlon = df['endlongitude'][(df['endlongitude'] > 75) & (df['endlongitude'] < 80)]
zero_end = ((df['endlatitude'] == 0) & (df['endlongitude'] == 0)).sum()
report4.append(f"- **Valid end coordinates**: {len(valid_endlat):,}")
report4.append(f"- **Zero-zero (no endpoint)**: {zero_end:,}")
if len(valid_endlat) > 0:
    report4.append(f"- **End Lat range**: {valid_endlat.min():.6f} to {valid_endlat.max():.6f}")
    report4.append(f"- **End Lon range**: {valid_endlon.min():.6f} to {valid_endlon.max():.6f}")

# Resolved location
report4.append("\n### Resolved Location (resolved_at_latitude, resolved_at_longitude)\n")
resolved_lat = df['resolved_at_latitude'].dropna()
resolved_lon = df['resolved_at_longitude'].dropna()
report4.append(f"- **Records with resolved coordinates**: {len(resolved_lat):,}")
if len(resolved_lat) > 0:
    valid_rlat = resolved_lat[(resolved_lat > 10) & (resolved_lat < 15)]
    report4.append(f"- **Valid resolved coords**: {len(valid_rlat):,}")

# Corridor distribution
report4.append("\n## Corridor Distribution\n")
corridor_vc = df['corridor'].value_counts(dropna=False)
report4.append(f"**Total unique corridors**: {df['corridor'].nunique()}\n")
report4.append("| Corridor | Count | % |")
report4.append("|----------|-------|---|")
for val, cnt in corridor_vc.items():
    pct = cnt / len(df) * 100
    report4.append(f"| {val} | {cnt:,} | {pct:.1f}% |")

# Zone distribution
report4.append("\n## Zone Distribution\n")
zone_vc = df['zone'].value_counts(dropna=False)
report4.append(f"**Total unique zones**: {df['zone'].nunique()}\n")
report4.append("| Zone | Count | % |")
report4.append("|------|-------|---|")
for val, cnt in zone_vc.items():
    pct = cnt / len(df) * 100
    val_str = str(val)[:60]
    report4.append(f"| {val_str} | {cnt:,} | {pct:.1f}% |")

# Junction analysis
report4.append("\n## Junction Analysis\n")
junction_non_null = df['junction'].notna().sum()
report4.append(f"**Records with junction info**: {junction_non_null:,} ({junction_non_null/len(df)*100:.1f}%)\n")
if junction_non_null > 0:
    junction_vc = df['junction'].value_counts().head(30)
    report4.append(f"**Unique junctions**: {df['junction'].nunique()}\n")
    report4.append("### Top 30 Junctions\n")
    report4.append("| Junction | Count | % |")
    report4.append("|----------|-------|---|")
    for val, cnt in junction_vc.items():
        pct = cnt / len(df) * 100
        report4.append(f"| {val} | {cnt:,} | {pct:.1f}% |")

# Police station distribution
report4.append("\n## Police Station Distribution\n")
ps_vc = df['police_station'].value_counts(dropna=False).head(30)
report4.append(f"**Unique police stations**: {df['police_station'].nunique()}\n")
report4.append("### Top 30 Police Stations\n")
report4.append("| Police Station | Count | % |")
report4.append("|---------------|-------|---|")
for val, cnt in ps_vc.items():
    pct = cnt / len(df) * 100
    val_str = str(val)[:50]
    report4.append(f"| {val_str} | {cnt:,} | {pct:.1f}% |")

# GBA Identifier
report4.append("\n## GBA Identifier Distribution\n")
gba_vc = df['gba_identifier'].value_counts(dropna=False)
report4.append(f"**Unique GBA identifiers**: {df['gba_identifier'].nunique()}\n")
report4.append("| GBA Identifier | Count | % |")
report4.append("|---------------|-------|---|")
for val, cnt in gba_vc.items():
    pct = cnt / len(df) * 100
    val_str = str(val)[:60]
    report4.append(f"| {val_str} | {cnt:,} | {pct:.1f}% |")

# Spatial event cause heatmap: which corridors have what types
report4.append("\n## Event Cause × Corridor Cross-tab (Top 10 corridors)\n")
top_corridors = df['corridor'].value_counts().head(10).index.tolist()
top_causes = df['event_cause'].value_counts().head(8).index.tolist()
ct = pd.crosstab(df[df['corridor'].isin(top_corridors)]['corridor'],
                 df[df['corridor'].isin(top_corridors)]['event_cause'])
ct = ct[[c for c in top_causes if c in ct.columns]]
# Manual markdown table
header = "| Corridor | " + " | ".join(str(c) for c in ct.columns) + " |"
sep = "|---" * (len(ct.columns) + 1) + "|"
report4.append(header)
report4.append(sep)
for idx in ct.index:
    row_vals = " | ".join(str(ct.loc[idx, c]) for c in ct.columns)
    report4.append(f"| {idx} | {row_vals} |")

(REPORT_DIR / "geography_report.md").write_text("\n".join(report4))
print("  ✅ geography_report.md written")

# ========================================================================
# REPORT 5: TEMPORAL REPORT
# ========================================================================
print("\n=== Generating Report 5: Temporal Report ===")

report5 = []
report5.append("# ⏰ Temporal Report\n")

# Date range
report5.append("## Date Range\n")
for col in temporal_cols:
    if col in df.columns:
        non_null = df[col].notna().sum()
        if non_null > 0:
            report5.append(f"- **{col}**: {df[col].min()} → {df[col].max()} ({non_null:,} non-null)")
        else:
            report5.append(f"- **{col}**: all null")

# Focus on start_datetime
start = df['start_datetime'].dropna()
report5.append(f"\n**Primary time range**: {start.min()} to {start.max()}")
report5.append(f"**Duration span**: {(start.max() - start.min()).days} days\n")

# Monthly distribution
report5.append("## Monthly Distribution (start_datetime)\n")
df['month'] = df['start_datetime'].dt.to_period('M')
month_vc = df['month'].value_counts().sort_index()
report5.append("| Month | Count | % |")
report5.append("|-------|-------|---|")
for val, cnt in month_vc.items():
    pct = cnt / len(df) * 100
    report5.append(f"| {val} | {cnt:,} | {pct:.1f}% |")

# Day of week
report5.append("\n## Day of Week Distribution\n")
df['dow'] = df['start_datetime'].dt.day_name()
dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
dow_vc = df['dow'].value_counts().reindex(dow_order)
report5.append("| Day | Count | % |")
report5.append("|-----|-------|---|")
for val, cnt in dow_vc.items():
    if pd.notna(cnt):
        pct = cnt / len(df) * 100
        report5.append(f"| {val} | {int(cnt):,} | {pct:.1f}% |")

# Hourly distribution
report5.append("\n## Hourly Distribution (24h)\n")
df['hour'] = df['start_datetime'].dt.hour
hour_vc = df['hour'].value_counts().sort_index()
report5.append("| Hour | Count | % | Bar |")
report5.append("|------|-------|---|-----|")
max_h = hour_vc.max() if len(hour_vc) > 0 else 1
for h in range(24):
    cnt = hour_vc.get(h, 0)
    pct = cnt / len(df) * 100
    bar = "█" * int(cnt / max_h * 30)
    report5.append(f"| {h:02d}:00 | {cnt:,} | {pct:.1f}% | {bar} |")

# Peak hours
report5.append("\n### Peak Hours Analysis\n")
if len(hour_vc) > 0:
    top3_hours = hour_vc.nlargest(3)
    bottom3_hours = hour_vc.nsmallest(3)
    report5.append("**Top 3 busiest hours**:")
    for h, c in top3_hours.items():
        report5.append(f"- {int(h):02d}:00 → {c:,} events")
    report5.append("\n**Bottom 3 quietest hours**:")
    for h, c in bottom3_hours.items():
        report5.append(f"- {int(h):02d}:00 → {c:,} events")

# Time to resolve analysis
report5.append("\n## Time-to-Resolve Analysis\n")

# Calculate resolution times
df['time_to_resolve_hours'] = None
# Use resolved_datetime if available, otherwise closed_datetime
if 'resolved_datetime' in df.columns and 'start_datetime' in df.columns:
    resolved_mask = df['resolved_datetime'].notna() & df['start_datetime'].notna()
    df.loc[resolved_mask, 'time_to_resolve_hours'] = (
        (df.loc[resolved_mask, 'resolved_datetime'] - df.loc[resolved_mask, 'start_datetime']).dt.total_seconds() / 3600
    )

if 'closed_datetime' in df.columns and 'start_datetime' in df.columns:
    closed_mask = df['closed_datetime'].notna() & df['start_datetime'].notna() & df['time_to_resolve_hours'].isna()
    df.loc[closed_mask, 'time_to_resolve_hours'] = (
        (df.loc[closed_mask, 'closed_datetime'] - df.loc[closed_mask, 'start_datetime']).dt.total_seconds() / 3600
    )

df['time_to_resolve_hours'] = pd.to_numeric(df['time_to_resolve_hours'], errors='coerce')
resolve_valid = df['time_to_resolve_hours'].dropna()
resolve_positive = resolve_valid[resolve_valid > 0]

report5.append(f"- **Records with resolution time**: {len(resolve_valid):,}")
report5.append(f"- **Records with positive resolution time**: {len(resolve_positive):,}")
if len(resolve_positive) > 0:
    report5.append(f"- **Mean resolution time**: {resolve_positive.mean():.1f} hours")
    report5.append(f"- **Median resolution time**: {resolve_positive.median():.1f} hours")
    report5.append(f"- **Std resolution time**: {resolve_positive.std():.1f} hours")
    report5.append(f"- **Min resolution time**: {resolve_positive.min():.2f} hours")
    report5.append(f"- **Max resolution time**: {resolve_positive.max():.1f} hours")
    report5.append(f"- **25th percentile**: {resolve_positive.quantile(0.25):.2f} hours")
    report5.append(f"- **75th percentile**: {resolve_positive.quantile(0.75):.2f} hours")
    report5.append(f"- **90th percentile**: {resolve_positive.quantile(0.90):.2f} hours")
    report5.append(f"- **95th percentile**: {resolve_positive.quantile(0.95):.2f} hours")
    
    # Negative times (anomalies)
    negative_times = resolve_valid[resolve_valid < 0]
    report5.append(f"\n- **⚠️ Negative resolution times**: {len(negative_times):,} (data quality issue)")

# Resolution time by event cause
report5.append("\n### Resolution Time by Event Cause\n")
if len(resolve_positive) > 0:
    resolve_by_cause = df[df['time_to_resolve_hours'] > 0].groupby('event_cause')['time_to_resolve_hours'].agg(['mean', 'median', 'count']).sort_values('count', ascending=False)
    report5.append("| Event Cause | Count | Mean (hrs) | Median (hrs) |")
    report5.append("|-------------|-------|-----------|-------------|")
    for cause, row in resolve_by_cause.iterrows():
        report5.append(f"| {cause} | {int(row['count']):,} | {row['mean']:.1f} | {row['median']:.1f} |")

# Resolution time by priority
report5.append("\n### Resolution Time by Priority\n")
if len(resolve_positive) > 0:
    resolve_by_pri = df[df['time_to_resolve_hours'] > 0].groupby('priority')['time_to_resolve_hours'].agg(['mean', 'median', 'count']).sort_values('count', ascending=False)
    report5.append("| Priority | Count | Mean (hrs) | Median (hrs) |")
    report5.append("|----------|-------|-----------|-------------|")
    for pri, row in resolve_by_pri.iterrows():
        report5.append(f"| {pri} | {int(row['count']):,} | {row['mean']:.1f} | {row['median']:.1f} |")

# Created vs Start datetime gap
report5.append("\n## Created vs Start DateTime Gap\n")
if 'created_date' in df.columns:
    create_gap_mask = df['created_date'].notna() & df['start_datetime'].notna()
    create_gap = (df.loc[create_gap_mask, 'created_date'] - df.loc[create_gap_mask, 'start_datetime']).dt.total_seconds() / 60
    report5.append(f"- **Records with both**: {create_gap_mask.sum():,}")
    if create_gap_mask.sum() > 0:
        report5.append(f"- **Mean gap**: {create_gap.mean():.1f} minutes")
        report5.append(f"- **Median gap**: {create_gap.median():.1f} minutes")
        report5.append(f"- **Negative gaps (created before start)**: {(create_gap < 0).sum():,}")

# Event type by time of day
report5.append("\n## Event Type by Time of Day\n")
time_bins = [(0, 6, 'Night (0-6)'), (6, 12, 'Morning (6-12)'), (12, 18, 'Afternoon (12-18)'), (18, 24, 'Evening (18-24)')]
df['time_period'] = pd.cut(df['hour'], bins=[0, 6, 12, 18, 24], labels=['Night', 'Morning', 'Afternoon', 'Evening'], right=False)
ct_time = pd.crosstab(df['event_type'], df['time_period'])
# Manual markdown table
header2 = "| Event Type | " + " | ".join(str(c) for c in ct_time.columns) + " |"
sep2 = "|---" * (len(ct_time.columns) + 1) + "|"
report5.append(header2)
report5.append(sep2)
for idx in ct_time.index:
    row_vals2 = " | ".join(str(ct_time.loc[idx, c]) for c in ct_time.columns)
    report5.append(f"| {idx} | {row_vals2} |")

(REPORT_DIR / "temporal_report.md").write_text("\n".join(report5))
print("  ✅ temporal_report.md written")

# ========================================================================
# REPORT 6: TARGET DEFINITION
# ========================================================================
print("\n=== Generating Report 6: Target Definition ===")

report6 = []
report6.append("# 🎯 Target Definition Report\n")
report6.append("## What Can We Predict?\n")
report6.append("Analysis of potential prediction targets for the hackathon.\n")

# Target 1: Road Closure
report6.append("---\n### Target 1: Road Closure Prediction (`requires_road_closure`)\n")
rc_vc = df['requires_road_closure'].value_counts(dropna=False)
report6.append("**Distribution**:\n")
report6.append("| Value | Count | % |")
report6.append("|-------|-------|---|")
for val, cnt in rc_vc.items():
    pct = cnt / len(df) * 100
    report6.append(f"| {val} | {cnt:,} | {pct:.1f}% |")
report6.append(f"\n**Feasibility**: {'⚠️ Highly imbalanced' if rc_vc.min() / rc_vc.max() < 0.2 else '✅ Reasonable balance'}")
report6.append("**Type**: Binary Classification")
report6.append("**Usable features**: event_cause, corridor, priority, hour, day_of_week, zone, description\n")

# Target 2: Event Type
report6.append("---\n### Target 2: Event Type Classification (`event_type`)\n")
et_vc = df['event_type'].value_counts()
report6.append("**Distribution**:\n")
report6.append("| Value | Count | % |")
report6.append("|-------|-------|---|")
for val, cnt in et_vc.items():
    pct = cnt / len(df) * 100
    report6.append(f"| {val} | {cnt:,} | {pct:.1f}% |")
report6.append(f"\n**Feasibility**: {'⚠️ Highly imbalanced' if et_vc.min() / et_vc.max() < 0.05 else '✅ Reasonable'}")
report6.append("**Type**: Multi-class Classification")

# Target 3: Priority
report6.append("\n---\n### Target 3: Priority Prediction (`priority`)\n")
pri_vc = df['priority'].value_counts(dropna=False)
report6.append("**Distribution**:\n")
report6.append("| Value | Count | % |")
report6.append("|-------|-------|---|")
for val, cnt in pri_vc.items():
    pct = cnt / len(df) * 100
    report6.append(f"| {val} | {cnt:,} | {pct:.1f}% |")
report6.append("\n**Type**: Ordinal Classification")

# Target 4: Resolution Time
report6.append("\n---\n### Target 4: Resolution Time Prediction\n")
if len(resolve_positive) > 0:
    report6.append(f"- **Usable records**: {len(resolve_positive):,} ({len(resolve_positive)/len(df)*100:.1f}%)")
    report6.append(f"- **Mean**: {resolve_positive.mean():.1f} hours")
    report6.append(f"- **Median**: {resolve_positive.median():.1f} hours")
    report6.append(f"- **Skewness**: {resolve_positive.skew():.2f}")
    
    # Binned for classification
    bins = [0, 0.5, 1, 2, 4, 12, 24, float('inf')]
    labels = ['<30min', '30min-1h', '1-2h', '2-4h', '4-12h', '12-24h', '>24h']
    binned = pd.cut(resolve_positive, bins=bins, labels=labels)
    report6.append("\n**Binned distribution (for classification approach)**:\n")
    report6.append("| Bin | Count | % |")
    report6.append("|-----|-------|---|")
    for label in labels:
        cnt = (binned == label).sum()
        pct = cnt / len(resolve_positive) * 100
        report6.append(f"| {label} | {cnt:,} | {pct:.1f}% |")
    
report6.append("\n**Type**: Regression or Binned Classification")
report6.append("**Usable features**: event_cause, event_type, corridor, priority, hour, day_of_week, zone, veh_type\n")

# Target 5: Event Cause
report6.append("---\n### Target 5: Event Cause Prediction (`event_cause`)\n")
ec_vc = df['event_cause'].value_counts()
report6.append("**Distribution**:\n")
report6.append("| Value | Count | % |")
report6.append("|-------|-------|---|")
for val, cnt in ec_vc.items():
    pct = cnt / len(df) * 100
    report6.append(f"| {val} | {cnt:,} | {pct:.1f}% |")
report6.append("\n**Type**: Multi-class Classification\n")

# Target 6: Congestion/Incident Hotspot prediction
report6.append("---\n### Target 6: Spatial-Temporal Hotspot Prediction\n")
report6.append("**Concept**: Predict where and when the next incident will occur\n")
report6.append("**Approach**: Grid the city into spatial bins, predict incident count per bin per time window\n")
report6.append("**Features**: Historical patterns, corridor, zone, junction, time features\n")
report6.append("**Type**: Regression (count prediction) or Classification (high/low risk)\n")

# Cross-feature predictive power
report6.append("\n---\n## Feature Correlation with Targets\n")
report6.append("### Road Closure by Event Cause\n")
rc_by_cause = pd.crosstab(df['event_cause'], df['requires_road_closure'], normalize='index') * 100
report6.append("\n| Event Cause | FALSE % | TRUE % |")
report6.append("|-------------|---------|--------|")
for cause in rc_by_cause.index:
    f_pct = rc_by_cause.loc[cause, False] if False in rc_by_cause.columns else 0
    t_pct = rc_by_cause.loc[cause, True] if True in rc_by_cause.columns else 0
    report6.append(f"| {cause} | {f_pct:.1f}% | {t_pct:.1f}% |")

# Road closure by priority
report6.append("\n### Road Closure by Priority\n")
rc_by_pri = pd.crosstab(df['priority'], df['requires_road_closure'], normalize='index') * 100
report6.append("\n| Priority | FALSE % | TRUE % |")
report6.append("|----------|---------|--------|")
for pri in rc_by_pri.index:
    f_pct = rc_by_pri.loc[pri, False] if False in rc_by_pri.columns else 0
    t_pct = rc_by_pri.loc[pri, True] if True in rc_by_pri.columns else 0
    report6.append(f"| {pri} | {f_pct:.1f}% | {t_pct:.1f}% |")

# Recommended target
report6.append("\n---\n## 🏆 Recommended Targets for Hackathon\n")
report6.append("""
| Rank | Target | Type | Records | Why |
|------|--------|------|---------|-----|
| 1 | **Resolution Time** | Regression | {} | High business impact, good feature set |
| 2 | **Road Closure** | Binary Classification | {} | Clear binary target, actionable |
| 3 | **Priority** | Ordinal Classification | {} | Good for triage automation |
| 4 | **Event Cause** | Multi-class | {} | Useful for dispatching |
| 5 | **Hotspot Prediction** | Spatial-Temporal | {} | Proactive traffic management |
""".format(
    f"{len(resolve_positive):,}",
    f"{len(df):,}",
    f"{df['priority'].notna().sum():,}",
    f"{df['event_cause'].notna().sum():,}",
    f"{len(df):,}"
))

(REPORT_DIR / "target_definition.md").write_text("\n".join(report6))
print("  ✅ target_definition.md written")

# ========================================================================
# REPORT 7: DATA QUALITY REPORT
# ========================================================================
print("\n=== Generating Report 7: Data Quality Report ===")

report7 = []
report7.append("# 🔍 Data Quality Report\n")

# Issue 1: Duplicate IDs
report7.append("## 1. Duplicate Analysis\n")
dup_ids = df['id'].duplicated().sum()
report7.append(f"- **Duplicate IDs**: {dup_ids}")
report7.append(f"- **Unique IDs**: {df['id'].nunique():,}")
report7.append(f"- **Total rows**: {len(df):,}")
if dup_ids > 0:
    dup_examples = df[df['id'].duplicated(keep=False)]['id'].value_counts().head(5)
    report7.append(f"- **Top duplicated IDs**: {dict(dup_examples)}")

# Issue 2: Coordinate anomalies
report7.append("\n## 2. Coordinate Anomalies\n")
lat_zero = (df['latitude'] == 0).sum()
lon_zero = (df['longitude'] == 0).sum()
lat_out = ((df['latitude'] < 12) | (df['latitude'] > 14)).sum()
lon_out = ((df['longitude'] < 76) | (df['longitude'] > 78.5)).sum()
endlat_zero = (df['endlatitude'] == 0).sum()
endlon_zero = (df['endlongitude'] == 0).sum()

report7.append(f"- **latitude == 0**: {lat_zero}")
report7.append(f"- **longitude == 0**: {lon_zero}")
report7.append(f"- **latitude outside Bengaluru (12-14)**: {lat_out}")
report7.append(f"- **longitude outside Bengaluru (76-78.5)**: {lon_out}")
report7.append(f"- **endlatitude == 0**: {endlat_zero}")
report7.append(f"- **endlongitude == 0**: {endlon_zero}")
report7.append(f"\n> ⚠️ {endlat_zero} records have (0,0) end coordinates — likely unused/not applicable\n")

# Issue 3: Temporal anomalies
report7.append("## 3. Temporal Anomalies\n")

# Future dates
now = pd.Timestamp.now(tz='UTC')
if df['start_datetime'].notna().any():
    future_starts = (df['start_datetime'] > now).sum()
    report7.append(f"- **Future start_datetime**: {future_starts}")

# End before start
if 'end_datetime' in df.columns:
    end_before_start = ((df['end_datetime'].notna()) & (df['start_datetime'].notna()) & (df['end_datetime'] < df['start_datetime'])).sum()
    report7.append(f"- **end_datetime before start_datetime**: {end_before_start}")

# Negative resolution times
if len(resolve_valid) > 0:
    neg_resolve = (resolve_valid < 0).sum()
    report7.append(f"- **Negative resolution times**: {neg_resolve}")

# Very long resolution (>30 days)
if len(resolve_positive) > 0:
    very_long = (resolve_positive > 720).sum()  # 30 days
    report7.append(f"- **Resolution > 30 days**: {very_long}")
    extremely_long = (resolve_positive > 2160).sum()  # 90 days
    report7.append(f"- **Resolution > 90 days**: {extremely_long}")

# Issue 4: Status consistency
report7.append("\n## 4. Status Consistency\n")
status_vc = df['status'].value_counts()
report7.append("**Status distribution**:\n")
for val, cnt in status_vc.items():
    report7.append(f"- `{val}`: {cnt:,}")

# Closed but no closed_datetime
if 'closed_datetime' in df.columns:
    closed_no_dt = ((df['status'] == 'closed') & (df['closed_datetime'].isna())).sum()
    report7.append(f"\n- **Status='closed' but no closed_datetime**: {closed_no_dt}")

# Resolved but no resolved_datetime
if 'resolved_datetime' in df.columns:
    resolved_no_dt = ((df['status'] == 'resolved') & (df['resolved_datetime'].isna())).sum()
    report7.append(f"- **Status='resolved' but no resolved_datetime**: {resolved_no_dt}")

# Open with resolved_datetime
if 'resolved_datetime' in df.columns:
    open_with_resolved = ((df['status'] == 'open') & (df['resolved_datetime'].notna())).sum()
    report7.append(f"- **Status='open' but has resolved_datetime**: {open_with_resolved}")

# Issue 5: Text quality
report7.append("\n## 5. Text Field Quality\n")
if 'description' in df.columns:
    desc_non_null = df['description'].notna().sum()
    if desc_non_null > 0:
        desc_lens = df['description'].dropna().str.len()
        very_short = (desc_lens < 5).sum()
        very_long_desc = (desc_lens > 500).sum()
        has_kannada = df['description'].dropna().str.contains(r'[\u0C80-\u0CFF]', regex=True, na=False).sum()
        report7.append(f"- **Descriptions available**: {desc_non_null:,}")
        report7.append(f"- **Very short (<5 chars)**: {very_short}")
        report7.append(f"- **Very long (>500 chars)**: {very_long_desc}")
        report7.append(f"- **Contains Kannada text**: {has_kannada:,}")

# Issue 6: Constant/near-constant columns
report7.append("\n## 6. Low-Variance Columns\n")
for col in df.columns:
    nunique = df[col].nunique()
    non_null = df[col].notna().sum()
    if nunique <= 1 and non_null > 0:
        val = df[col].dropna().iloc[0] if non_null > 0 else 'N/A'
        report7.append(f"- **`{col}`**: constant value = `{val}` ({non_null:,} non-null)")
    elif nunique == 2 and non_null > 0:
        vc = df[col].value_counts()
        dominant_pct = vc.iloc[0] / non_null * 100
        if dominant_pct > 95:
            report7.append(f"- **`{col}`**: near-constant, dominant value `{vc.index[0]}` = {dominant_pct:.1f}%")

# Issue 7: Anonymized fields
report7.append("\n## 7. Anonymized Fields Analysis\n")
anon_cols = ['id', 'veh_no', 'created_by_id', 'last_modified_by_id', 'assigned_to_police_id', 
             'citizen_accident_id', 'closed_by_id', 'resolved_by_id', 'kgid', 'gba_identifier']
for col in anon_cols:
    if col in df.columns:
        non_null = df[col].notna().sum()
        nunique = df[col].nunique()
        report7.append(f"- **`{col}`**: {non_null:,} non-null, {nunique:,} unique")

# Issue 8: Vehicle data quality
report7.append("\n## 8. Vehicle Data Quality\n")
if 'veh_type' in df.columns:
    veh_non_null = df['veh_type'].notna().sum()
    report7.append(f"- **veh_type populated**: {veh_non_null:,} ({veh_non_null/len(df)*100:.1f}%)")
    if veh_non_null > 0:
        report7.append(f"- **Unique vehicle types**: {df['veh_type'].nunique()}")
        vc = df['veh_type'].value_counts()
        for v, c in vc.items():
            report7.append(f"  - `{v}`: {c:,}")

if 'veh_no' in df.columns:
    vehno_non_null = df['veh_no'].notna().sum()
    report7.append(f"- **veh_no populated**: {vehno_non_null:,} ({vehno_non_null/len(df)*100:.1f}%)")

# Breakdown specific fields
report7.append("\n### Breakdown-specific fields (should correlate with event_cause=vehicle_breakdown)\n")
breakdown_mask = df['event_cause'] == 'vehicle_breakdown'
non_breakdown_mask = df['event_cause'] != 'vehicle_breakdown'
for col in ['cargo_material', 'reason_breakdown', 'age_of_truck']:
    if col in df.columns:
        in_breakdown = df.loc[breakdown_mask, col].notna().sum()
        out_breakdown = df.loc[non_breakdown_mask, col].notna().sum()
        report7.append(f"- **`{col}`**: {in_breakdown} in breakdowns, {out_breakdown} in non-breakdowns")

# Issue 9: requires_road_closure type check
report7.append("\n## 9. Boolean Field Encoding\n")
if 'requires_road_closure' in df.columns:
    report7.append(f"- **`requires_road_closure`** unique values: {df['requires_road_closure'].unique().tolist()}")
    report7.append(f"- dtype: {df['requires_road_closure'].dtype}")
if 'authenticated' in df.columns:
    report7.append(f"- **`authenticated`** unique values: {df['authenticated'].unique().tolist()}")

# Issue 10: route_path and meta_data
report7.append("\n## 10. Complex Fields\n")
for col in ['route_path', 'meta_data']:
    if col in df.columns:
        non_null = df[col].notna().sum()
        report7.append(f"- **`{col}`**: {non_null:,} non-null ({non_null/len(df)*100:.1f}%)")
        if non_null > 0:
            sample = str(df[col].dropna().iloc[0])[:150]
            report7.append(f"  - Sample: `{sample}`")

# Recommendations
report7.append("\n---\n## 📋 Recommendations\n")
report7.append("""
### Data Cleaning
1. **Replace (0,0) end coordinates with NaN** — {endlat_zero:,} records have placeholder zeros
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
""".format(endlat_zero=endlat_zero))

(REPORT_DIR / "data_quality_report.md").write_text("\n".join(report7))
print("  ✅ data_quality_report.md written")

print("\n" + "="*60)
print("✅ ALL 7 REPORTS GENERATED SUCCESSFULLY")
print("="*60)
print(f"\nReports saved to: {REPORT_DIR}")
for f in sorted(REPORT_DIR.glob("*.md")):
    print(f"  📄 {f.name}")
