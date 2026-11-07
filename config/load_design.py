from __future__ import annotations

import json
from pathlib import Path


def load_design(path: str | None = None) -> dict:
    """
    Load optical design configuration JSON.

    If no path is provided, automatically load:
    optillm/design_input.json
    """

    if path is None:
        # project root = parent of config folder
        project_root = Path(__file__).resolve().parents[1]
        path = project_root / "design_input.json"
    else:
        path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"{path} not found")

    with open(path, "r") as f:
        cfg = json.load(f)

    return cfg


if __name__ == "__main__":
    cfg = load_design()
    print("Loaded design config:")
    print(cfg)