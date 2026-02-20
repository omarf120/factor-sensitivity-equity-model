# src/io_utils.py
from __future__ import annotations

from pathlib import Path
import pandas as pd


def read_parts(folder: Path, pattern: str, **read_csv_kwargs) -> pd.DataFrame:
    files = sorted(folder.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No files matched: {folder}/{pattern}")

    dfs = [pd.read_csv(f, **read_csv_kwargs) for f in files]
    return pd.concat(dfs, ignore_index=True).drop_duplicates()


def write_single_col_no_header(series: pd.Series, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    series.to_csv(out_path, index=False, header=False)