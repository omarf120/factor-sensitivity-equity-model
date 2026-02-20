# src/universe.py
from __future__ import annotations

from pathlib import Path
import pandas as pd


def build_universe_permnos(crsp_monthly_folder: Path, top_n: int = 1000) -> pd.Series:
    """
    Builds the PERMNO universe by taking top N by market cap from two CRSP monthly snapshots.
    Expects:
      crsp_monthly/snapshot_2003.csv
      crsp_monthly/snapshot_2024.csv
    """
    df_2003 = pd.read_csv(crsp_monthly_folder / "snapshot_2003.csv")
    df_2024 = pd.read_csv(crsp_monthly_folder / "snapshot_2024.csv")

    for df in (df_2003, df_2024):
        df["MKTCAP"] = df["PRC"].abs() * df["SHROUT"] * 1000.0  # SHROUT is in thousands

    top_2003 = (
        df_2003.sort_values("MKTCAP", ascending=False)
        .drop_duplicates("PERMNO")
        .head(top_n)
    )
    top_2024 = (
        df_2024.sort_values("MKTCAP", ascending=False)
        .drop_duplicates("PERMNO")
        .head(top_n)
    )

    permnos = (
        pd.concat([top_2003["PERMNO"], top_2024["PERMNO"]])
        .dropna()
        .astype(int)
        .drop_duplicates()
        .reset_index(drop=True)
    )
    return permnos