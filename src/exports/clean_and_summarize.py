#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import pandas as pd
import numpy as np


# -------------------------------------------------------
# RULES (pipeline column names)
# (low_outer, low_inner, high_inner, high_outer)
#
# NOTE: Your old rules were in your renamed units.
# These below assume:
#   - atq, ltq, seqq, saleq, niq are in $MM (Compustat quarterly)
#   - cshoq is in MM shares
#   - bv_ps and epspxq are per-share dollars
#   - adj_prc is per-share dollars
#   - weekly_log_ret_total is log return
# -------------------------------------------------------
RULES: dict[str, tuple[float, float, float, float]] = {
    # per-share
    "bv_ps":              (-25,   -10,    150,     300),
    "cf_ps":              (-15,   -5,     25,      100),
    "epspxq":             (-10,   -4,     10,      20),

    # $MM (Compustat)
    "saleq":              (0,     15,     25000,   50000),
    "seqq":               (-5000, -2000,  100000,  250000),
    "atq":                (0,     100,    400000,  800000),
    "ltq":                (0,     25,     400000,  800000),
    "sales_ps":           (0,      0,        150,     300),
    #"niq":                (-1000,   -500,  2000,     3000),

    # shares (MM shares)
    "cshoq":              (0,     10,     3000,     5000),    # 10MM–3000MM inner

    # weekly return
    "adj_prc": (0, 1, 20000, 50000),
    "weekly_log_ret_total": (-0.5, -0.5,  0.5,  0.5),
}

# -----------------------------------------
# English display names (for Excel table)
# -----------------------------------------
ENGLISH_NAMES: dict[str, str] = {
    "bv_ps": "Book Value per Share",
    "cf_ps": "Cash Flow per Share",
    "epspxq": "Earnings per Share (Compustat EPSPXQ)",
    "sales_ps": "Sales per Share",
    "saleq": "Total Sales (Quarterly, $MM)",
    "seqq": "Shareholders' Equity (Quarterly, $MM)",
    "atq": "Total Assets (Quarterly, $MM)",
    "ltq": "Total Liabilities (Quarterly, $MM)",
    "cshoq": "Shares Outstanding (Quarterly, MM shares)",
    "weekly_log_ret_total": "Weekly Log Return (Total Return)",
    "adj_prc": "Adjusted Price (CRSP)",
    #"niq": "Net Income (Quarterly, $MM)"
}

def display_metric_name(metric: str) -> str:
    return ENGLISH_NAMES.get(metric, metric)

# Always keep these columns (not cleaned, just retained)
KEEP_ID_COLS = ["PERMNO", "date", "datadate"]


# -----------------------------
# Paths (repo-relative)
# -----------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]  # src/cleaning/... -> repo root
IN_PATH   = REPO_ROOT / "data" / "processed" / "final_factor_panel_raw.csv"
OUT_CLEAN = REPO_ROOT / "data" / "processed" / "final_factor_panel_raw_clean.csv"
OUT_XLSX  = REPO_ROOT / "outputs" / "tables" / "winsor_trunc_summary_raw.xlsx"


@dataclass
class GlobalSummary:
    total_raw_uncleaned_rows: int
    total_raw_after_trunc_wins: int
    rows_truncated: int
    pct_rows_truncated: float


def apply_rules(
    df: pd.DataFrame,
    rules: dict[str, tuple[float, float, float, float]]
) -> tuple[pd.DataFrame, pd.DataFrame, GlobalSummary]:
    """
    Order-invariant cleaning:

    1) Outer truncation (row drops) is computed per metric on the *raw* df,
       then applied ONCE using the union of all truncation masks.
    2) Inner winsorization (clipping) is applied per metric on the truncated df.
    3) NaNs are never truncated/winsorized; they pass through unchanged.

    Returns:
      clean_df: df after global outer truncation + per-metric winsorization
      stats_df: per-metric trunc/winsor stats
      global_summary: overall truncation counts/percent
    """
    n_raw = len(df)
    df_work = df.copy()

    # --- Validate columns exist ---
    missing_cols = [c for c in rules.keys() if c not in df_work.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # --- Per-metric outer trunc masks on RAW df ---
    trunc_masks: dict[str, pd.Series] = {}
    stats_rows: list[dict] = []

    for col, (lo_out, lo_in, hi_in, hi_out) in rules.items():
        s = df_work[col]

        low_trunc_mask  = s.notna() & (s < lo_out)
        high_trunc_mask = s.notna() & (s > hi_out)
        trunc_mask = low_trunc_mask | high_trunc_mask

        trunc_masks[col] = trunc_mask

        n_low_trunc  = int(low_trunc_mask.sum())
        n_high_trunc = int(high_trunc_mask.sum())
        n_trunc      = int(trunc_mask.sum())

        pct_low_trunc  = 100.0 * n_low_trunc  / n_raw if n_raw else 0.0
        pct_high_trunc = 100.0 * n_high_trunc / n_raw if n_raw else 0.0
        pct_trunc      = 100.0 * n_trunc      / n_raw if n_raw else 0.0

        stats_rows.append({
            "Metric": col,
            "Rows Before": n_raw,          # same baseline for all metrics (raw df)
            # "Rows After Trunc" filled after we apply global truncation
            "Low Outer": lo_out,
            "Low Inner": lo_in,
            "High Inner": hi_in,
            "High Outer": hi_out,
            "Trunc Low (n)": n_low_trunc,
            "Trunc High (n)": n_high_trunc,
            "Trunc Total (n)": n_trunc,
            "Trunc Low (%)": round(pct_low_trunc, 4),
            "Trunc High (%)": round(pct_high_trunc, 4),
            "Trunc Total (%)": round(pct_trunc, 4),
            # winsor fields filled after truncation
            "Wins Low (n)": 0,
            "Wins High (n)": 0,
            "Wins Low (%)": 0.0,
            "Wins High (%)": 0.0,
        })

    # --- Global outer truncation: drop ONCE (union of masks) ---
    if trunc_masks:
        global_trunc_mask = np.logical_or.reduce([m.values for m in trunc_masks.values()])
        global_trunc_mask = pd.Series(global_trunc_mask, index=df_work.index)
    else:
        global_trunc_mask = pd.Series(False, index=df_work.index)

    rows_before_any = len(df_work)
    df_work = df_work.loc[~global_trunc_mask].copy()
    n_after_trunc = len(df_work)

    rows_truncated = rows_before_any - n_after_trunc
    pct_rows_truncated = 100.0 * rows_truncated / rows_before_any if rows_before_any else 0.0

    # --- Inner winsorization on truncated df (no row drops) ---
    # Build a lookup for stats_rows by metric for easy updates
    stats_by_metric = {row["Metric"]: row for row in stats_rows}

    for col, (lo_out, lo_in, hi_in, hi_out) in rules.items():
        s2 = df_work[col]

        low_win_mask  = s2.notna() & (s2 < lo_in)
        high_win_mask = s2.notna() & (s2 > hi_in)

        n_low_win  = int(low_win_mask.sum())
        n_high_win = int(high_win_mask.sum())

        pct_low_win  = 100.0 * n_low_win  / n_after_trunc if n_after_trunc else 0.0
        pct_high_win = 100.0 * n_high_win / n_after_trunc if n_after_trunc else 0.0

        # clip
        df_work.loc[low_win_mask, col] = lo_in
        df_work.loc[high_win_mask, col] = hi_in

        # update stats
        row = stats_by_metric[col]
        row["Rows After Trunc"] = n_after_trunc
        row["Wins Low (n)"] = n_low_win
        row["Wins High (n)"] = n_high_win
        row["Wins Low (%)"] = round(pct_low_win, 4)
        row["Wins High (%)"] = round(pct_high_win, 4)

    # Ensure every row has Rows After Trunc (in case rules empty)
    for row in stats_rows:
        row.setdefault("Rows After Trunc", n_after_trunc)

    global_summary = GlobalSummary(
        total_raw_uncleaned_rows=n_raw,
        total_raw_after_trunc_wins=n_after_trunc,
        rows_truncated=rows_truncated,
        pct_rows_truncated=pct_rows_truncated,
    )

    stats_df = pd.DataFrame(stats_rows)
    return df_work, stats_df, global_summary

def build_paper_table(
    stats_df: pd.DataFrame,
    global_summary: GlobalSummary
) -> pd.DataFrame:
    """
    Builds the exact table you asked for:
    Metric | % Low Trunc | % Low Wind | Low outer | Low inner | High inner | High outer |
            % High Wind | % High Trunc | Total % Trunc | Total % Wind
    plus the 3 global rows at the bottom.
    """
    t = stats_df.copy()

    # Convert to the exact columns you want
    out = pd.DataFrame({
        "Metric": t["Metric"].map(display_metric_name),
        "% Low Trunc": t["Trunc Low (%)"],
        "% Low Wind": t["Wins Low (%)"],
        "Low outer limit": t["Low Outer"],
        "Low inner limit": t["Low Inner"],
        "High inner limit": t["High Inner"],
        "High outer limit": t["High Outer"],
        "% High Wind": t["Wins High (%)"],
        "% High Trunc": t["Trunc High (%)"],
        "Total % Trunc": (t["Trunc Low (%)"] + t["Trunc High (%)"]).round(4),
        "Total % Wind": (t["Wins Low (%)"] + t["Wins High (%)"]).round(4),
    })

    # Append global summary rows at bottom (same columns; blanks where not relevant)
    summary_rows = pd.DataFrame([
        {"Metric": "Total Raw Uncleaned Rows", "% Low Trunc": global_summary.total_raw_uncleaned_rows},
        {"Metric": "Total Raw Cleaned Rows", "% Low Trunc": global_summary.total_raw_after_trunc_wins},
        {"Metric": "% Truncated", "% Low Trunc": round(global_summary.pct_rows_truncated, 2)},
    ])

    # Ensure all columns exist in summary_rows
    for c in out.columns:
        if c not in summary_rows.columns:
            summary_rows[c] = ""

    # Reorder summary columns to match
    summary_rows = summary_rows[out.columns]

    final = pd.concat([out, summary_rows], ignore_index=True)

    # Match your example formatting precision
    pct_cols = ["% Low Trunc", "% Low Wind", "% High Wind", "% High Trunc", "Total % Trunc", "Total % Wind"]
    for c in pct_cols:
        # keep ints for the bottom rows; format floats to 3 decimals
        final[c] = final[c].apply(lambda x: round(float(x), 3) if isinstance(x, (float, np.floating)) else x)

    return final

def safe_div(numer: pd.Series, denom: pd.Series) -> pd.Series:
    denom2 = denom.where(denom.notna() & (denom != 0))
    out = numer / denom2
    return out.replace([np.inf, -np.inf], np.nan)

def main() -> None:
    OUT_CLEAN.parent.mkdir(parents=True, exist_ok=True)
    OUT_XLSX.parent.mkdir(parents=True, exist_ok=True)

    if not IN_PATH.exists():
        raise FileNotFoundError(f"Missing input file: {IN_PATH}")

    df = pd.read_csv(IN_PATH, low_memory=False)

    # Keep ID cols + rule cols (only those that exist)
    keep_cols = [c for c in KEEP_ID_COLS if c in df.columns] + list(RULES.keys())
    missing = [c for c in RULES.keys() if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in input: {missing}")

    df = df[keep_cols].copy()

    # Apply trunc + wins
    df_clean, stats_df, global_summary = apply_rules(df, RULES)

    # Derive relevant value and quality ratios for analysis
    df_clean["bvp"] = safe_div(df_clean["bv_ps"], df_clean["adj_prc"])
    df_clean["ep"]  = safe_div(df_clean["epspxq"], df_clean["adj_prc"])
    df_clean["cfp"] = safe_div(df_clean["cf_ps"], df_clean["adj_prc"])
    df_clean["sp"]  = safe_div(df_clean["sales_ps"], df_clean["adj_prc"])
    df_clean["roa"] = safe_div((df_clean["epspxq"] * df_clean["cshoq"]), df_clean["atq"])
    df_clean["roe"] = safe_div((df_clean["epspxq"] * df_clean["cshoq"] ), df_clean["seqq"])
    df_clean["cf_sales"] = safe_div(df_clean["cf_ps"], df_clean["sales_ps"])

    df_clean_no_na = df_clean.copy()
    rows_dropped_na = 0
    rows_after_na = len(df_clean_no_na)

    # Save cleaned dataset
    df_clean_no_na.to_csv(OUT_CLEAN, index=False)

    summary_table = pd.DataFrame([
        {"Item": "Total Raw Uncleaned Rows", "Value": global_summary.total_raw_uncleaned_rows},
        {"Item": "Total Raw After Trunc/Wins Rows", "Value": global_summary.total_raw_after_trunc_wins},
        {"Item": "Rows Truncated (outer)", "Value": global_summary.rows_truncated},
        {"Item": "% Truncated (outer)", "Value": round(global_summary.pct_rows_truncated, 4)},
        {"Item": "Rows Dropped due to NaNs (after cleaning)", "Value": rows_dropped_na},
        {"Item": "Final Rows Saved", "Value": rows_after_na},
    ])

    paper_table = build_paper_table(stats_df, global_summary)

    with pd.ExcelWriter(OUT_XLSX, engine="openpyxl") as writer:
        summary_table.to_excel(writer, sheet_name="Summary", index=False)
        stats_df.to_excel(writer, sheet_name="Per_Metric", index=False)
        paper_table.to_excel(writer, sheet_name="Paper_Table", index=False)

    print(f"[OK] Read:  {IN_PATH}  (n={len(df):,})")
    print(f"[OK] Wrote: {OUT_CLEAN} (n={rows_after_na:,})")
    print(f"[OK] Wrote: {OUT_XLSX}")


if __name__ == "__main__":
    main()