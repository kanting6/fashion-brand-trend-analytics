from __future__ import annotations

from pathlib import Path
import typer
from rich.console import Console

from fashion_trends.settings import settings
from fashion_trends.db import connect
from fashion_trends.pipelines.generate_data import GenConfig, generate_synthetic_data
from fashion_trends.pipelines.ingest import ingest_raw_csvs
from fashion_trends.pipelines.run_sql import run_sql_folder
from fashion_trends.pipelines.compute_indices import compute_and_store_indices
from fashion_trends.pipelines.export_tableau import export_csvs

app = typer.Typer(add_completion=False)
console = Console()


@app.command("generate-data")
def generate_data_cmd() -> None:
    """Generate synthetic raw CSVs into RAW_DIR (default: data/raw)."""
    settings.ensure_dirs()
    generate_synthetic_data(
        GenConfig(seed=settings.seed, days=settings.days, n_users=settings.n_users, out_dir=settings.raw_dir)
    )
    console.print(f"[green]Raw data generated in {settings.raw_dir}.[/green]")


@app.command()
def ingest() -> None:
    """Ingest raw CSVs into DuckDB raw schema."""
    settings.ensure_dirs()
    con = connect(settings.db_path)
    ingest_raw_csvs(con, settings.raw_dir)
    console.print("[green]Ingest complete.[/green]")


@app.command("run-sql")
def run_sql_cmd() -> None:
    """Run SQL transforms (staging + marts) into DuckDB."""
    settings.ensure_dirs()
    con = connect(settings.db_path)
    run_sql_folder(con, Path("sql"))
    console.print("[green]SQL transforms complete.[/green]")


@app.command("compute-indices")
def compute_indices_cmd() -> None:
    """Compute trend indices (Python) and store to mart.mart_brand_trend_index."""
    settings.ensure_dirs()
    con = connect(settings.db_path)
    compute_and_store_indices(con)
    console.print("[green]Trend indices stored.[/green]")


@app.command("export-tableau")
def export_tableau_cmd() -> None:
    """Export Tableau-ready CSV extracts."""
    settings.ensure_dirs()
    con = connect(settings.db_path)
    export_csvs(con, settings.export_dir)
    console.print(f"[green]Exports written to {settings.export_dir}.[/green]")


@app.command("demo-existing")
def demo_existing_cmd() -> None:
    """Run pipeline assuming raw CSVs already exist in RAW_DIR (e.g., data/sample)."""
    ingest()
    run_sql_cmd()
    compute_indices_cmd()
    export_tableau_cmd()
    console.print("[bold green]Demo (existing data) complete.[/bold green]")


@app.command()
def demo() -> None:
    """Generate data + run the full pipeline end-to-end."""
    generate_data_cmd()
    demo_existing_cmd()
