from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Settings:
    db_path: Path = Path(os.getenv("DB_PATH", "warehouse/warehouse.duckdb"))
    raw_dir: Path = Path(os.getenv("RAW_DIR", "data/raw"))
    export_dir: Path = Path(os.getenv("EXPORT_DIR", "exports/tableau"))
    seed: int = int(os.getenv("SEED", "7"))
    days: int = int(os.getenv("DAYS", "210"))
    n_users: int = int(os.getenv("N_USERS", "80000"))

    def ensure_dirs(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.export_dir.mkdir(parents=True, exist_ok=True)

settings = Settings()
