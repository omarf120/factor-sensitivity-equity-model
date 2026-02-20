# src/run_pipeline.py
from __future__ import annotations

from .config import get_paths
from .io_utils import write_single_col_no_header
from .universe import build_universe_permnos
from .ccm_link import load_and_clean_ccm_link, extract_linked_ids
from .crsp_daily import load_and_clean_crsp_daily
from .compustat_quarterly import load_and_clean_compustat_quarterly
from .crsp_weekly import build_weekly_crsp_panel
from .merge_panel import link_fundamentals_to_permno, merge_weekly_with_fundamentals
from .factors import compute_factors


def main() -> None:
    paths = get_paths()
    paths.processed.mkdir(parents=True, exist_ok=True)

    # 1) Universe
    permnos = build_universe_permnos(paths.crsp_monthly)
    write_single_col_no_header(permnos, paths.processed / "universe_permnos.csv")
    print(f"[OK] universe_permnos.csv: n={len(permnos)}")

    # 2) Link table
    link = load_and_clean_ccm_link(paths.ccm_link)
    gvkeys, linked_permnos = extract_linked_ids(link)
    write_single_col_no_header(gvkeys, paths.processed / "linked_gvkeys.csv")
    write_single_col_no_header(linked_permnos, paths.processed / "linked_permnos.csv")
    print(f"[OK] linked_gvkeys.csv: n={len(gvkeys)}")
    print(f"[OK] linked_permnos.csv: n={len(linked_permnos)}")

    # 3) CRSP daily -> weekly
    prices = load_and_clean_crsp_daily(paths.crsp_daily)
    weekly = build_weekly_crsp_panel(prices)
    weekly_out = paths.processed / "crsp_weekly_panel.csv"
    weekly.to_csv(weekly_out, index=False)
    print(f"[OK] crsp_weekly_panel.csv: {weekly.shape}")

    # 4) Compustat fundamentals -> link -> merge
    fundamentals = load_and_clean_compustat_quarterly(paths.compustat_q)
    funda_linked = link_fundamentals_to_permno(fundamentals, link)
    merged = merge_weekly_with_fundamentals(weekly, funda_linked)

    # 5) Compute factors
    panel = compute_factors(merged)
    out = paths.processed / "final_factor_panel_raw.csv"
    panel.to_csv(out, index=False)
    print(f"[OK] final_factor_panel_raw.csv: {panel.shape}")


if __name__ == "__main__":
    main()