# src/factors.py
from __future__ import annotations

import numpy as np
import pandas as pd


def compute_factors(panel: pd.DataFrame) -> pd.DataFrame:
    panel = panel.sort_values(["PERMNO", "date"]).copy()

    # market cap in dollars (raw)
    panel["mktcap"] = panel["PRC"].abs() * panel["SHROUT"] * 1000.0
    panel["mktcap_m"] = panel["mktcap"] / 1e6

    den_csh = panel["cshoq"].replace({0: np.nan})

    panel["bv_ps"] = panel["ceqq"] / den_csh
    panel["cf_ps"] = panel["oancfy"] / den_csh
    panel["sales_ps"] = panel["saleq"] / den_csh

    # trailing 53-week dividend yield
    panel["div_trailing"] = (
        panel.groupby("PERMNO", sort=False)["D_t_adj"]
        .apply(lambda s: s.rolling(53, min_periods=1).sum())
        .reset_index(level=0, drop=True)
    )
    panel["div_yield"] = panel["div_trailing"] / panel["adj_prc"].replace({0: np.nan})

    return panel