from __future__ import annotations

import json
from pathlib import Path

from config.load_design import load_design


def update_json(d_low_nm: float, d_high_nm: float, path: str = "design_input.json") -> None:
    project_root = Path(__file__).resolve().parents[1]
    p = project_root / path

    cfg = load_design()  # reads from project root automatically
    # Store in structure (match your schema)
    cfg["structure"]["d1_nm"] = float(d_low_nm)   # low-index thickness
    cfg["structure"]["d2_nm"] = float(d_high_nm)  # high-index thickness

    with open(p, "w") as f:
        json.dump(cfg, f, indent=2)

    print(f"Updated {p} with d1_nm and d2_nm.")


if __name__ == "__main__":
    # Paste the values you just got from BO:
    d_low_nm = 161.541955
    d_high_nm = 104.736659
    update_json(d_low_nm, d_high_nm)