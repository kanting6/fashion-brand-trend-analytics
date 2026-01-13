-- DuckDB macro for safe division
CREATE OR REPLACE MACRO safe_divide(n, d) AS
  CASE
    WHEN d IS NULL OR d = 0 THEN NULL
    ELSE (n * 1.0) / d
  END;
