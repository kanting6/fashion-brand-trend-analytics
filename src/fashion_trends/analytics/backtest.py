from __future__ import annotations

import numpy as np
import pandas as pd


def baseline_trigger_week(series: pd.Series, *, window: int = 8, threshold: float = 0.02) -> int | None:
    """Naive baseline: 8-week moving average crosses a threshold."""
    ma = series.rolling(window=window, min_periods=window).mean()
    trig = np.where(ma.to_numpy() >= threshold)[0]
    return int(trig[0]) if len(trig) else None


def trend_index_trigger_week(series: pd.Series, threshold: float = 1.5) -> int | None:
    trig = np.where(series.to_numpy() >= threshold)[0]
    return int(trig[0]) if len(trig) else None


def compute_lead_time_weeks(
    index_df: pd.DataFrame,
    *,
    group_cols: list[str],
    metric: str = "conversion_rate",
    index_col: str = "trend_index",
    week_col: str = "week_start",
) -> pd.DataFrame:
    df = index_df[index_df["metric"] == metric].copy()
    if df.empty:
        return pd.DataFrame()

    df = df.sort_values(group_cols + [week_col])
    out = []
    for keys, g in df.groupby(group_cols, sort=False):
        g = g.sort_values(week_col)
        thresh = float(g["baseline_mean"].median() + 0.005)
        baseline_w = baseline_trigger_week(g["recent_mean"], threshold=thresh)
        index_w = trend_index_trigger_week(g[index_col], threshold=1.5)
        if baseline_w is None or index_w is None:
            continue
        out.append(
            {
                **{c: v for c, v in zip(group_cols, keys if isinstance(keys, tuple) else (keys,))},
                "lead_time_weeks": int(baseline_w - index_w),
            }
        )
    return pd.DataFrame(out)
