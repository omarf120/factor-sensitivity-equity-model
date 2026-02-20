# src/config.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Paths:
    root: Path
    raw: Path
    processed: Path
    outputs: Path

    crsp_monthly: Path
    crsp_daily: Path
    compustat_q: Path
    ccm_link: Path


def get_paths() -> Paths:
    """
    Repo structure: repo_root/src/config.py
    """
    root = Path(__file__).resolve().parents[1]
    raw = root / "data" / "raw"
    processed = root / "data" / "processed"
    outputs = root / "outputs"

    return Paths(
        root=root,
        raw=raw,
        processed=processed,
        outputs=outputs,
        crsp_monthly=raw / "crsp_monthly",
        crsp_daily=raw / "crsp_daily",
        compustat_q=raw / "compustat_quarterly",
        ccm_link=raw / "ccm_link",
    )