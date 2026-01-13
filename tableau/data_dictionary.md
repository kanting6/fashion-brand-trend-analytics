# Data Dictionary

## brand_weekly_performance
- week_start (DATE)
- region (NA/EU/APAC)
- brand, category, gender
- traffic_sessions, atc_sessions, purchase_sessions
- atc_rate, conversion_rate
- units_sold, revenue_gross
- discount_dependency, return_rate, avg_markdown_pct

## collection_health
- week_start, region, brand, category, gender, collection
- units_received, units_sold, sell_through
- revenue_gross, discount_dependency, return_rate, avg_markdown_pct

## style_weekly
- week_start, region, brand, gender, category, silhouette, color
- traffic_sessions, atc_sessions, purchase_sessions
- atc_rate, conversion_rate

## brand_trend_index
- week_start + style dims + metric
- trend_index, is_emerging, is_fatiguing
- lead_time_weeks (nullable)
