# src/compustat_quarterly.py
from __future__ import annotations

from pathlib import Path
import pandas as pd

from .io_utils import read_parts


def load_and_clean_compustat_quarterly(compustat_q_folder: Path) -> pd.DataFrame:
    """
    Loads Compustat quarterly fundamentals from parts.
    Expects pattern: fundamentals_part*.csv
    """
    funda = read_parts(compustat_q_folder, "fundamentals_part*.csv", low_memory=False)

    funda["datadate"] = pd.to_datetime(funda["datadate"], errors="coerce")
    funda["rdq"] = pd.to_datetime(funda.get("rdq"), errors="coerce")

    numeric_cols = ["niq", "atq", "seqq", "ceqq", "saleq", "oancfy", "cshoq", "epspxq"]
    for col in numeric_cols:
        if col in funda.columns:
            funda[col] = pd.to_numeric(funda[col], errors="coerce")

    funda = (
        funda.sort_values(["gvkey", "datadate", "rdq"], na_position="first")
        .drop_duplicates(subset=["gvkey", "datadate"], keep="last")
        .reset_index(drop=True)
    )
    return funda