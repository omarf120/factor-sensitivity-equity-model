# src/crsp_daily.py
from __future__ import annotations

from pathlib import Path
import pandas as pd

from .io_utils import read_parts


def load_and_clean_crsp_daily(crsp_daily_folder: Path) -> pd.DataFrame:
    """
    Loads CRSP daily stock file from parts and does basic cleaning.
    Expects pattern: daily_part*.csv
    Required columns used later:
      PERMNO, date, PRC, CFACPR, SHROUT, CFACSHR, VOL, RET, DIVAMT, DISTCD, PAYDT
    """
    prices = read_parts(crsp_daily_folder, "daily_part*.csv", low_memory=False)

    prices["date"] = pd.to_datetime(prices["date"], errors="coerce")
    prices["PAYDT"] = pd.to_datetime(prices.get("PAYDT"), errors="coerce")

    prices["RET"] = pd.to_numeric(prices.get("RET"), errors="coerce")
    prices["PRC"] = pd.to_numeric(prices.get("PRC"), errors="coerce").abs()

    prices = prices.sort_values(["PERMNO", "date"]).reset_index(drop=True)
    return prices