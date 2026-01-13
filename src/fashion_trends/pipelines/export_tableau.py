from __future__ import annotations

from pathlib import Path
import duckdb
from rich.console import Console

console = Console()

EXPORTS = {
    "brand_weekly_performance": "SELECT * FROM mart.mart_brand_weekly_performance",
    "collection_health": "SELECT * FROM mart.mart_collection_health",
    "style_weekly": "SELECT * FROM mart.mart_style_weekly",
    "brand_trend_index": "SELECT * FROM mart.mart_brand_trend_index",
}


def export_csvs(con: duckdb.DuckDBPyConnection, export_dir: Path) -> None:
    export_dir.mkdir(parents=True, exist_ok=True)
    for name, sql in EXPORTS.items():
        out = export_dir / f"{name}.csv"
        console.print(f"[bold]Exporting[/bold] {name} → {out}")
        con.execute(f"COPY ({sql}) TO '{out.as_posix()}' (HEADER, DELIMITER ',');")
