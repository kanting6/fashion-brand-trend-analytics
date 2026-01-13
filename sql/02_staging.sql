CREATE OR REPLACE VIEW staging.stg_products AS
SELECT
  CAST(product_id AS BIGINT) AS product_id,
  brand,
  category,
  gender,
  collection,
  silhouette,
  color,
  CAST(list_price AS DOUBLE) AS list_price
FROM raw.products;

CREATE OR REPLACE VIEW staging.stg_inventory_receipts AS
SELECT
  CAST(product_id AS BIGINT) AS product_id,
  CAST(week_start AS DATE) AS week_start,
  CAST(units_received AS BIGINT) AS units_received
FROM raw.inventory_receipts;

CREATE OR REPLACE VIEW staging.stg_web_events AS
WITH base AS (
  SELECT
    CAST(ts AS TIMESTAMP) AS ts,
    CAST(date AS DATE) AS event_date,
    CAST(user_id AS BIGINT) AS user_id,
    session_id,
    region,
    event_type,
    CAST(product_id AS BIGINT) AS product_id
  FROM raw.web_events
)
SELECT
  *,
  DATE_TRUNC('week', event_date)::DATE AS week_start
FROM base;

CREATE OR REPLACE VIEW staging.stg_orders AS
WITH orders AS (
  SELECT
    CAST(order_id AS BIGINT) AS order_id,
    CAST(order_ts AS TIMESTAMP) AS order_ts,
    CAST(user_id AS BIGINT) AS user_id,
    region,
    CAST(discount_pct AS DOUBLE) AS discount_pct,
    DATE_TRUNC('week', CAST(order_ts AS DATE))::DATE AS week_start
  FROM raw.orders
),
items AS (
  SELECT
    CAST(order_id AS BIGINT) AS order_id,
    CAST(product_id AS BIGINT) AS product_id,
    CAST(quantity AS BIGINT) AS quantity,
    CAST(unit_price AS DOUBLE) AS unit_price,
    CAST(markdown_pct AS DOUBLE) AS markdown_pct,
    CAST(is_returned AS BIGINT) AS is_returned
  FROM raw.order_items
)
SELECT
  o.*,
  i.product_id,
  i.quantity,
  i.unit_price,
  i.markdown_pct,
  i.is_returned,
  (i.quantity * i.unit_price) AS gross_revenue
FROM orders o
JOIN items i USING (order_id);
