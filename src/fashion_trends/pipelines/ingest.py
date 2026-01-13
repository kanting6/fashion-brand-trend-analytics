from __future__ import annotations

from pathlib import Path
import duckdb
from rich.console import Console

from fashion_trends.db import bootstrap_schemas

console = Console()


def ingest_raw_csvs(con: duckdb.DuckDBPyConnection, raw_dir: Path) -> None:
    """Loads raw CSVs into DuckDB raw schema."""
    bootstrap_schemas(con)

    mapping = {
        "products": raw_dir / "products.csv",
        "inventory_receipts": raw_dir / "inventory_receipts.csv",
        "web_events": raw_dir / "web_events.csv",
        "orders": raw_dir / "orders.csv",
        "order_items": raw_dir / "order_items.csv",
    }

    for table, path in mapping.items():
        if not path.exists():
            raise FileNotFoundError(f"Missing {path}. Run generate-data first.")
        console.print(f"[bold]Loading[/bold] raw.{table} ← {path}")
        con.execute(f"DROP TABLE IF EXISTS raw.{table};")
        con.execute(
            "CREATE TABLE raw.{t} AS SELECT * FROM read_csv_auto('{p}', HEADER=TRUE);".format(
                t=table, p=path.as_posix()
            )
        )
