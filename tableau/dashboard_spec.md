# Tableau Dashboard Spec (Merchandising & Content Strategy)

Data sources (exported by pipeline):
- `exports/tableau/brand_weekly_performance.csv`
- `exports/tableau/collection_health.csv`
- `exports/tableau/style_weekly.csv`
- `exports/tableau/brand_trend_index.csv`

## Dashboard 1 — Brand Overview
- KPI strip: Traffic Sessions, ATC Rate, Conversion Rate, Revenue, Return Rate
- Brand leaderboard: conversion_rate by brand (filters: region, gender, category, week range)
- Funnel trend over time
- Promo sensitivity: discount_dependency vs conversion_rate (scatter)

## Dashboard 2 — Collection Health
- Sell-through by collection (heatmap)
- Markdown dependency by brand/collection
- Returns watchlist by brand/category/collection

## Dashboard 3 — Trend Radar
- Emerging styles: is_emerging=True; size=traffic_sessions; color=trend_index
- Fatiguing styles: is_fatiguing=True
- Lead-time: histogram of lead_time_weeks
