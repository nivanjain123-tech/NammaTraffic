# Gridlock_Round2 Folder Map

## Current Structure (Post-Reorganization)

```
Gridlock_Round2/
├── data_inventory.json              # Phase 1: Complete file inventory
├── folder_map.md                    # Phase 1: This file — folder structure reference
├── theme_scoring.md                 # Phase 2: Theme comparison scoring matrix
├── theme_scoring.json               # Phase 2: Machine-readable theme scores
├── archive_manifest.json            # Phase 3: Record of all file moves
│
├── selected_theme/                  # ✅ ACTIVE WORKSPACE — Event-Driven Congestion
│   ├── Astram event data_anonymized...csv   # Primary dataset: 8204 incidents
│   └── theme_event_congestion.png           # Problem statement screenshot
│
├── archive_other_themes/            # 🗂️ ARCHIVED — Rejected themes
│   ├── parking/
│   │   ├── jan to may police violation...csv  # 298K parking violations
│   │   └── theme_parking_congestion.png       # Parking theme screenshot
│   └── computer_vision/
│       └── theme_cv_violations.png            # CV theme screenshot
│
├── reports/                         # 📊 All analysis & architecture reports
│   ├── dataset_overview.md
│   ├── missing_values_report.md
│   ├── feature_catalog.md
│   ├── geography_report.md
│   ├── temporal_report.md
│   ├── target_definition.md
│   ├── data_quality_report.md
│   ├── architecture_overview.md
│   ├── frontend_architecture.md
│   ├── backend_architecture.md
│   ├── ml_architecture.md
│   ├── gis_architecture.md
│   ├── database_schema.md
│   ├── api_design.md
│   ├── deployment_architecture.md
│   ├── ai_copilot_design.md
│   ├── demo_script.md
│   ├── 24_hour_plan.md
│   ├── 48_hour_plan.md
│   └── final_submission_checklist.md
│
├── artifacts/                       # 📈 Plots, figures, intermediate outputs
│
├── code/                            # 💻 All source code and scripts
│
├── logs/                            # 📝 Decision logs, prompt versions
│
└── handover_bundle/                 # 📦 Complete handover for other AI models
    ├── README.md
    ├── project_summary.md
    ├── theme_decision.md
    └── prompt_version.txt
```

## File Purpose Guide

| File/Folder | Purpose |
|---|---|
| `selected_theme/` | Contains ONLY files for the chosen theme (Event-Driven Congestion) |
| `archive_other_themes/` | Contains rejected themes' files, organized by theme |
| `reports/` | All markdown reports — data audit, architecture, plans |
| `artifacts/` | Generated plots, charts, analysis outputs |
| `code/` | Python scripts, notebooks, pipeline code |
| `logs/` | Decision logs, prompt versions, change history |
| `handover_bundle/` | Self-contained package for transferring to other AI models |
