from __future__ import annotations

from pathlib import Path
import duckdb
from rich.console import Console

from fashion_trends.db import bootstrap_schemas

console = Console()


def run_sql_folder(con: duckdb.DuckDBPyConnection, sql_dir: Path) -> None:
    """Executes all .sql files in a folder (sorted by filename)."""
    bootstrap_schemas(con)
    if not sql_dir.exists():
        raise FileNotFoundError(sql_dir)

    sql_files = sorted([p for p in sql_dir.glob("*.sql") if p.is_file()])
    if not sql_files:
        raise RuntimeError(f"No SQL files found in {sql_dir}")

    for p in sql_files:
        console.print(f"[bold]Running SQL[/bold] {p}")
        con.execute(p.read_text(encoding="utf-8"))
