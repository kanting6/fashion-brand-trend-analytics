import pandas as pd
from fashion_trends.analytics.trend_index import compute_trend_index, TrendIndexConfig


def test_trend_index_runs_and_flags_emerging():
    df = pd.DataFrame(
        {
            "week_start": pd.date_range("2025-01-06", periods=24, freq="W-MON"),
            "brand": ["A"] * 24,
            "region": ["NA"] * 24,
            "gender": ["W"] * 24,
            "category": ["Tops"] * 24,
            "silhouette": ["Slim"] * 24,
            "color": ["Black"] * 24,
            "traffic_sessions": [500] * 24,
            "atc_rate": [0.06] * 12 + [0.06 + 0.002*i for i in range(12)],
            "conversion_rate": [0.015] * 12 + [0.015 + 0.001*i for i in range(12)],
        }
    )
    cfg = TrendIndexConfig(min_sessions=100, emerging_threshold=1.0)
    out = compute_trend_index(
        df,
        metric_col="conversion_rate",
        group_cols=["brand","region","gender","category","silhouette","color"],
        cfg=cfg,
    )
    assert len(out) > 0
    assert out["is_emerging"].any()
