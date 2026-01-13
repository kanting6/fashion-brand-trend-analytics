-- Weekly funnel by brand/category/gender/region
CREATE OR REPLACE TABLE mart.mart_brand_weekly_funnel AS
SELECT
  w.week_start,
  w.region,
  p.brand,
  p.category,
  p.gender,
  COUNT(DISTINCT CASE WHEN event_type='page_view' THEN session_id END) AS traffic_sessions,
  COUNT(DISTINCT CASE WHEN event_type='add_to_cart' THEN session_id END) AS atc_sessions,
  COUNT(DISTINCT CASE WHEN event_type='purchase' THEN session_id END) AS purchase_sessions,
  safe_divide(
    COUNT(DISTINCT CASE WHEN event_type='add_to_cart' THEN session_id END),
    COUNT(DISTINCT CASE WHEN event_type='page_view' THEN session_id END)
  ) AS atc_rate,
  safe_divide(
    COUNT(DISTINCT CASE WHEN event_type='purchase' THEN session_id END),
    COUNT(DISTINCT CASE WHEN event_type='page_view' THEN session_id END)
  ) AS conversion_rate
FROM staging.stg_web_events w
JOIN staging.stg_products p USING (product_id)
GROUP BY 1,2,3,4,5;

-- Weekly sales + returns + markdown dependency (collection grain)
CREATE OR REPLACE TABLE mart.mart_collection_health AS
WITH sales AS (
  SELECT
    o.week_start,
    o.region,
    p.brand,
    p.category,
    p.gender,
    p.collection,
    SUM(o.quantity) AS units_sold,
    SUM(o.gross_revenue) AS revenue_gross,
    SUM(CASE WHEN o.markdown_pct > 0.05 THEN o.gross_revenue ELSE 0 END) AS revenue_discounted,
    SUM(o.is_returned) AS units_returned,
    AVG(o.markdown_pct) AS avg_markdown_pct
  FROM staging.stg_orders o
  JOIN staging.stg_products p USING (product_id)
  GROUP BY 1,2,3,4,5,6
),
inv AS (
  SELECT
    week_start,
    p.brand,
    p.category,
    p.gender,
    p.collection,
    SUM(units_received) AS units_received
  FROM staging.stg_inventory_receipts r
  JOIN staging.stg_products p USING (product_id)
  GROUP BY 1,2,3,4,5
)
SELECT
  s.*,
  inv.units_received,
  safe_divide(s.units_sold, inv.units_received) AS sell_through,
  safe_divide(s.revenue_discounted, s.revenue_gross) AS discount_dependency,
  safe_divide(s.units_returned, s.units_sold) AS return_rate
FROM sales s
LEFT JOIN inv
  ON s.week_start = inv.week_start
 AND s.brand = inv.brand
 AND s.category = inv.category
 AND s.gender = inv.gender
 AND s.collection = inv.collection;

-- Brand performance (weekly): join funnel + aggregated collection sales
CREATE OR REPLACE TABLE mart.mart_brand_weekly_performance AS
WITH sales AS (
  SELECT
    week_start,
    region,
    brand,
    category,
    gender,
    SUM(units_sold) AS units_sold,
    SUM(revenue_gross) AS revenue_gross,
    SUM(revenue_discounted) AS revenue_discounted,
    SUM(units_returned) AS units_returned,
    AVG(avg_markdown_pct) AS avg_markdown_pct,
    AVG(discount_dependency) AS discount_dependency,
    AVG(return_rate) AS return_rate
  FROM mart.mart_collection_health
  GROUP BY 1,2,3,4,5
)
SELECT
  f.week_start,
  f.region,
  f.brand,
  f.category,
  f.gender,
  f.traffic_sessions,
  f.atc_sessions,
  f.purchase_sessions,
  f.atc_rate,
  f.conversion_rate,
  s.units_sold,
  s.revenue_gross,
  safe_divide(s.revenue_gross, NULLIF(f.purchase_sessions, 0)) AS revenue_per_purchase_session,
  s.discount_dependency,
  s.return_rate,
  s.avg_markdown_pct
FROM mart.mart_brand_weekly_funnel f
LEFT JOIN sales s
  ON f.week_start = s.week_start
 AND f.region = s.region
 AND f.brand = s.brand
 AND f.category = s.category
 AND f.gender = s.gender;

-- Weekly style signals (silhouette + color) for trend detection
CREATE OR REPLACE TABLE mart.mart_style_weekly AS
SELECT
  e.week_start,
  e.region,
  p.brand,
  p.gender,
  p.category,
  p.silhouette,
  p.color,
  COUNT(DISTINCT CASE WHEN event_type='page_view' THEN session_id END) AS traffic_sessions,
  COUNT(DISTINCT CASE WHEN event_type='add_to_cart' THEN session_id END) AS atc_sessions,
  COUNT(DISTINCT CASE WHEN event_type='purchase' THEN session_id END) AS purchase_sessions,
  safe_divide(
    COUNT(DISTINCT CASE WHEN event_type='add_to_cart' THEN session_id END),
    COUNT(DISTINCT CASE WHEN event_type='page_view' THEN session_id END)
  ) AS atc_rate,
  safe_divide(
    COUNT(DISTINCT CASE WHEN event_type='purchase' THEN session_id END),
    COUNT(DISTINCT CASE WHEN event_type='page_view' THEN session_id END)
  ) AS conversion_rate
FROM staging.stg_web_events e
JOIN staging.stg_products p USING (product_id)
GROUP BY 1,2,3,4,5,6,7;
