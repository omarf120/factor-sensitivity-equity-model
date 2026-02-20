# src/crsp_weekly.py
from __future__ import annotations

import numpy as np
import pandas as pd


def build_weekly_crsp_panel(prices: pd.DataFrame, end_date: str = "2024-12-31") -> pd.DataFrame:
    """
    Builds weekly CRSP panel with:
      - weekly last price (W-WED)
      - adjusted price (adj_prc = |PRC| * CFACPR)
      - cash dividends summed by PAYDT within each Wed week, adjusted by CFACPR as-of pay date
      - weekly returns: price-only + total (incl divs)
    """
    prices = prices.copy()
    prices = prices.sort_values(["PERMNO", "date"])
    prices["date"] = pd.to_datetime(prices["date"])
    prices["PAYDT"] = pd.to_datetime(prices.get("PAYDT"), errors="coerce")

    # Weekly last observation (week ends Wednesday)
    weekly = (
        prices.set_index("date")
        .groupby("PERMNO")
        .resample("W-WED")
        .last()[["PRC", "CFACPR", "SHROUT", "CFACSHR", "VOL"]]
        .reset_index()
    )

    weekly["adj_prc"] = weekly["PRC"].abs() * weekly["CFACPR"]

    # Cash dividends only (DISTCD 1200–1299)
    is_cash = (prices["DISTCD"] >= 1200) & (prices["DISTCD"] < 1300)
    div = prices.loc[is_cash & prices["PAYDT"].notna(), ["PERMNO", "PAYDT", "DIVAMT"]].copy()
    div = div.sort_values(["PERMNO", "PAYDT"])

    # CFACPR as-of pay date (per PERMNO)
    cfac = prices[["PERMNO", "date", "CFACPR"]].dropna().sort_values(["PERMNO", "date"])
    div = pd.merge_asof(
        div.sort_values("PAYDT"),
        cfac.sort_values("date"),
        by="PERMNO",
        left_on="PAYDT",
        right_on="date",
        direction="backward",
    )
    div["CFACPR"] = div["CFACPR"].fillna(1.0)
    div["div_adj"] = div["DIVAMT"] * div["CFACPR"]

    div["week"] = div["PAYDT"].dt.to_period("W-WED").dt.to_timestamp("W-WED")
    wk_div = (
        div.groupby(["PERMNO", "week"], as_index=False)["div_adj"]
        .sum()
        .rename(columns={"week": "date", "div_adj": "D_t_adj"})
    )

    weekly = pd.merge(weekly, wk_div, on=["PERMNO", "date"], how="outer")
    weekly["D_t_adj"] = weekly["D_t_adj"].fillna(0.0)

    weekly = weekly.sort_values(["PERMNO", "date"]).reset_index(drop=True)

    # forward-fill price fields for dividend-only weeks
    ffill_cols = ["PRC", "CFACPR", "SHROUT", "CFACSHR", "VOL", "adj_prc"]
    weekly[ffill_cols] = weekly.groupby("PERMNO")[ffill_cols].ffill()

    # returns
    weekly["adj_prc_lag"] = weekly.groupby("PERMNO")["adj_prc"].shift(1)
    weekly["weekly_ret_price_only"] = weekly.groupby("PERMNO")["adj_prc"].pct_change(fill_method=None)

    weekly["weekly_log_ret_total"] = np.log((weekly["adj_prc"] + weekly["D_t_adj"]) / weekly["adj_prc_lag"])
    weekly["weekly_log_ret_price_only"] = np.log(weekly["adj_prc"] / weekly["adj_prc_lag"])

    # basic cleaning
    weekly = weekly[pd.to_datetime(weekly["date"]) <= pd.to_datetime(end_date)].reset_index(drop=True)
    weekly = weekly[weekly["adj_prc"].notna()]
    weekly = weekly[weekly["adj_prc_lag"] > 0]

    # extra fields you used later
    weekly["shares"] = weekly["SHROUT"] * 1000.0 / weekly["CFACSHR"]
    weekly["mktcap"] = weekly["PRC"] * weekly["shares"]

    # sanity: all Wednesdays
    assert (weekly["date"].dt.day_name() == "Wednesday").all()

    return weekly