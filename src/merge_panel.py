# src/merge_panel.py
from __future__ import annotations

import pandas as pd


def link_fundamentals_to_permno(
    fundamentals: pd.DataFrame,
    link: pd.DataFrame,
) -> pd.DataFrame:
    """
    Links Compustat fundamentals to PERMNO via CCM link, respecting LINKDT/LINKENDDT.
    Creates info_date = rdq if available else datadate.
    """
    link = link.copy()
    fundamentals = fundamentals.copy()

    # robust date handling
    link["LINKDT"] = pd.to_datetime(link["LINKDT"], errors="coerce").fillna(pd.Timestamp("1900-01-01"))
    link["LINKENDDT"] = pd.to_datetime(link["LINKENDDT"], errors="coerce").fillna(pd.Timestamp("2099-12-31"))

    fundamentals["gvkey"] = fundamentals["gvkey"].astype(str)
    link["GVKEY"] = link["GVKEY"].astype(str)

    funda_linked = fundamentals.merge(
        link[["GVKEY", "LPERMNO", "LINKDT", "LINKENDDT"]],
        left_on="gvkey",
        right_on="GVKEY",
        how="left",
    )

    # valid link period
    funda_linked = funda_linked[
        (funda_linked["datadate"] >= funda_linked["LINKDT"])
        & (funda_linked["datadate"] <= funda_linked["LINKENDDT"])
    ].copy()

    funda_linked = funda_linked.rename(columns={"LPERMNO": "PERMNO"})
    funda_linked["info_date"] = funda_linked["rdq"].fillna(funda_linked["datadate"])
    funda_linked["info_date"] = pd.to_datetime(funda_linked["info_date"], errors="coerce")

    return funda_linked


def merge_weekly_with_fundamentals(
    weekly: pd.DataFrame,
    funda_linked: pd.DataFrame,
) -> pd.DataFrame:
    """
    As-of merge weekly panel with fundamentals using info_date (backward), by PERMNO.
    """
    weekly = weekly.dropna(subset=["date"]).copy()
    funda_linked = funda_linked.dropna(subset=["info_date"]).copy()

    weekly = weekly.sort_values(["date", "PERMNO"]).reset_index(drop=True)
    funda_linked = funda_linked.sort_values(["info_date", "PERMNO"]).reset_index(drop=True)

    # ensure fundamentals don't extend past weekly max
    funda_linked = funda_linked[funda_linked["info_date"] <= weekly["date"].max()]

    merged = pd.merge_asof(
        weekly.sort_values(["date", "PERMNO"]),
        funda_linked.sort_values(["info_date", "PERMNO"]),
        by="PERMNO",
        left_on="date",
        right_on="info_date",
        direction="backward",
        allow_exact_matches=True,
    )

    # No lookahead check
    mask = merged["info_date"].notna() & merged["date"].notna()
    assert (merged.loc[mask, "info_date"] <= merged.loc[mask, "date"]).all()

    return merged