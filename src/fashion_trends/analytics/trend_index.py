from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class TrendIndexConfig:
    baseline_weeks: int = 12
    exclude_recent_weeks: int = 4
    recent_weeks: int = 3
    slope_weeks: int = 4
    min_sessions: int = 250
    emerging_threshold: float = 1.5
    fatiguing_threshold: float = -1.0


def _zscore(delta: float, baseline_std: float) -> float:
    if baseline_std is None or baseline_std <= 1e-9:
        return 0.0
    return float(delta / baseline_std)


def _slope(y: np.ndarray) -> float:
    if len(y) < 2:
        return 0.0
    x = np.arange(len(y), dtype=float)
    x = x - x.mean()
    y = y.astype(float) - y.mean()
    denom = float((x**2).sum())
    if denom <= 1e-12:
        return 0.0
    return float((x * y).sum() / denom)


def compute_trend_index(
    df: pd.DataFrame,
    *,
    metric_col: str,
    volume_col: str = "traffic_sessions",
    group_cols: list[str],
    week_col: str = "week_start",
    cfg: TrendIndexConfig = TrendIndexConfig(),
) -> pd.DataFrame:
    """Computes a z-like trend index per group using momentum + acceleration."""
    work = df.copy()
    work[week_col] = pd.to_datetime(work[week_col])
    work = work.sort_values(group_cols + [week_col])

    rows: list[dict] = []
    for keys, g in work.groupby(group_cols, sort=False):
        g = g.sort_values(week_col).reset_index(drop=True)
        y = g[metric_col].astype(float).to_numpy()
        vol = g[volume_col].astype(float).to_numpy()
        weeks = g[week_col].to_numpy()

        for i in range(len(g)):
            hist_start = max(0, i - (cfg.baseline_weeks + cfg.exclude_recent_weeks) + 1)
            baseline_end = i - cfg.exclude_recent_weeks
            if baseline_end <= hist_start or baseline_end <= 1:
                continue

            baseline = y[hist_start:baseline_end]
            baseline_mean = float(np.nanmean(baseline))
            baseline_std = (
                float(np.nanstd(baseline, ddof=1)) if len(baseline) >= 3 else float(np.nanstd(baseline))
            )

            recent_start = max(0, i - cfg.recent_weeks + 1)
            recent_mean = float(np.nanmean(y[recent_start : i + 1]))

            momentum = _zscore(recent_mean - baseline_mean, baseline_std)
            slope_start = max(0, i - cfg.slope_weeks + 1)
            accel = _zscore(_slope(y[slope_start : i + 1]), baseline_std)

            index = 0.65 * momentum + 0.35 * accel
            is_emerging = (index >= cfg.emerging_threshold) and (vol[i] >= cfg.min_sessions)

            row = {c: v for c, v in zip(group_cols, keys if isinstance(keys, tuple) else (keys,))}
            row.update(
                {
                    week_col: pd.Timestamp(weeks[i]),
                    "metric": metric_col,
                    "baseline_mean": baseline_mean,
                    "baseline_std": baseline_std,
                    "recent_mean": recent_mean,
                    "momentum_z": momentum,
                    "accel_z": accel,
                    "trend_index": float(index),
                    "traffic_sessions": float(vol[i]),
                    "is_emerging": bool(is_emerging),
                }
            )
            rows.append(row)

    return pd.DataFrame(rows)


def mark_fatigue(
    index_df: pd.DataFrame,
    *,
    group_cols: list[str],
    week_col: str = "week_start",
    cfg: TrendIndexConfig = TrendIndexConfig(),
) -> pd.DataFrame:
    """Marks fatigue if a style peaked recently and is now negative."""
    if index_df.empty:
        index_df["is_fatiguing"] = False
        return index_df

    w = index_df.sort_values(group_cols + [week_col]).copy()
    w["is_fatiguing"] = False
    for _, g in w.groupby(group_cols, sort=False):
        g = g.sort_values(week_col)
        peak_recent = g["trend_index"].rolling(window=12, min_periods=1).max()
        fatigue = (g["trend_index"] <= cfg.fatiguing_threshold) & (peak_recent >= cfg.emerging_threshold)
        w.loc[g.index, "is_fatiguing"] = fatigue.to_numpy()
    return w
