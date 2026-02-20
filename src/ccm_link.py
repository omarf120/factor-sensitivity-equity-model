# src/ccm_link.py
from __future__ import annotations

from pathlib import Path
import pandas as pd

from .io_utils import read_parts


def load_and_clean_ccm_link(ccm_link_folder: Path) -> pd.DataFrame:
    """
    Loads CCM link table from parts and cleans link dates/types.
    Expects pattern: ccm_link_part*.csv
    """
    link = read_parts(ccm_link_folder, "ccm_link_part*.csv")

    link["LINKENDDT"] = link["LINKENDDT"].replace("E", pd.NA)
    link["LINKDT"] = pd.to_datetime(link["LINKDT"], format="%m/%d/%y", errors="coerce")
    link["LINKENDDT"] = pd.to_datetime(link["LINKENDDT"], format="%m/%d/%y", errors="coerce")

    link["LINKENDDT"] = link["LINKENDDT"].fillna(pd.Timestamp.today().normalize())

    link = link[link["LINKTYPE"].isin(["LC", "LU"])].drop_duplicates()

    return link


def extract_linked_ids(link: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    gvkeys = link["GVKEY"].dropna().astype(str).drop_duplicates().sort_values().reset_index(drop=True)
    permnos = link["LPERMNO"].dropna().astype(int).drop_duplicates().sort_values().reset_index(drop=True)
    return gvkeys, permnos