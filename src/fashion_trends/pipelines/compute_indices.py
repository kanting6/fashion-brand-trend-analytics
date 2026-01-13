from __future__ import annotations

import duckdb
import pandas as pd
from rich.console import Console
from rich.table import Table

from fashion_trends.analytics.trend_index import TrendIndexConfig, compute_trend_index, mark_fatigue
from fashion_trends.analytics.backtest import compute_lead_time_weeks

console = Console()


def compute_and_store_indices(con: duckdb.DuckDBPyConnection, cfg: TrendIndexConfig = TrendIndexConfig()) -> None:
    df = con.execute("SELECT * FROM mart.mart_style_weekly").df()
    if df.empty:
        raise RuntimeError("mart.mart_style_weekly is empty. Run SQL transforms first (run-sql).")

    group_cols = ["brand", "region", "gender", "category", "silhouette", "color"]
    idx_conv = compute_trend_index(df, metric_col="conversion_rate", group_cols=group_cols, cfg=cfg)
    idx_atc = compute_trend_index(df, metric_col="atc_rate", group_cols=group_cols, cfg=cfg)

    idx = pd.concat([idx_conv, idx_atc], ignore_index=True)
    idx = mark_fatigue(idx, group_cols=group_cols + ["metric"], cfg=cfg)

    lead = compute_lead_time_weeks(idx, group_cols=group_cols, metric="conversion_rate")
    if not lead.empty:
        idx = idx.merge(lead, on=group_cols, how="left")

    con.execute("DROP TABLE IF EXISTS mart.mart_brand_trend_index;")
    con.register("idx_df", idx)
    con.execute("CREATE TABLE mart.mart_brand_trend_index AS SELECT * FROM idx_df;")

    _print_report(idx)


def _print_report(idx: pd.DataFrame) -> None:
    latest_week = idx["week_start"].max()
    latest = idx[idx["week_start"] == latest_week].copy()

    console.print(f"\n[bold cyan]Trend snapshot for week_start={latest_week.date()}[/bold cyan]\n")

    def show(flag: str, title: str, ascending: bool) -> None:
        t = Table(title=title)
        cols = ["brand", "region", "gender", "category", "silhouette", "color", "metric", "trend_index", "traffic_sessions", "lead_time_weeks"]
        for c in cols:
            t.add_column(c)
        view = latest[latest[flag] == True].sort_values("trend_index", ascending=ascending).head(12)
        for _, r in view.iterrows():
            t.add_row(
                str(r["brand"]), str(r["region"]), str(r["gender"]), str(r["category"]),
                str(r["silhouette"]), str(r["color"]), str(r["metric"]),
                f'{r["trend_index"]:.2f}', f'{r["traffic_sessions"]:.0f}',
                "" if pd.isna(r.get("lead_time_weeks")) else str(int(r["lead_time_weeks"])),
            )
        console.print(t)

    show("is_emerging", "Top Emerging Styles (early momentum)", ascending=False)
    show("is_fatiguing", "Top Fatiguing Styles (early fatigue)", ascending=True)
