from __future__ import annotations

import json
from pathlib import Path

import optuna

from config.load_design import load_design
from runner.bo_from_json import objective_factory
from runner.render_stack_from_json import render_stack
from physics.tmm_1d import spectrum
from physics.metrics import bandgap_metrics


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]  # optillm/


def _default_design_path() -> Path:
    return _project_root() / "design_input.json"


def _write_back_best(cfg: dict, d_low_nm: float, d_high_nm: float, input_path: str | Path) -> Path:
    """
    Save optimized thicknesses back into the SAME JSON file that was used as input.

    Convention:
      d1_nm = low-index thickness (materials[0])
      d2_nm = high-index thickness (materials[1])
    """
    cfg["structure"]["d1_nm"] = float(d_low_nm)
    cfg["structure"]["d2_nm"] = float(d_high_nm)

    out_path = Path(input_path)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

    return out_path


def main(json_path: str | None = None):
    # If no path is given, use the original default file
    if json_path is None:
        json_path = str(_default_design_path())

    # 1) Load JSON spec
    cfg = load_design(json_path)
    trials = int(cfg["optimization"].get("trials", 40))

    # 2) BO objective from JSON
    objective, const = objective_factory(cfg)

    # Repeatable demo runs
    sampler = optuna.samplers.TPESampler(seed=42)
    study = optuna.create_study(direction="minimize", sampler=sampler)
    study.optimize(objective, n_trials=trials)

    best = study.best_params
    scale = float(best["scale"])
    ratio = float(best["ratio"])

    # 3) Reconstruct best thicknesses
    d_low_nm = const["d_low_base"] * scale * ratio
    d_high_nm = const["d_high_base"] * scale / ratio

    print("\n=== OPTIMIZED DESIGN ===")
    print("Best params:", best)
    print(f"d_low_nm  = {d_low_nm:.6f}  (materials[0])")
    print(f"d_high_nm = {d_high_nm:.6f}  (materials[1])")

    # 4) Write back to the SAME JSON file used as input
    updated_json_path = _write_back_best(
        cfg,
        d_low_nm=d_low_nm,
        d_high_nm=d_high_nm,
        input_path=json_path
    )
    print("Updated JSON:", updated_json_path)

    # 5) Final physics validation (run once more)
    lambda0 = const["lambda0"]
    periods = const["periods"]
    order = const["order"]
    wavelengths = const["wavelengths"]

    if order == "HL":
        n_layers = [const["n_high"], const["n_low"]] * periods
        d_layers = [d_high_nm, d_low_nm] * periods
    else:
        n_layers = [const["n_low"], const["n_high"]] * periods
        d_layers = [d_low_nm, d_high_nm] * periods

    R, T = spectrum(const["n_a"], const["n_s"], n_layers, d_layers, wavelengths)
    m = bandgap_metrics(
        wavelengths,
        T,
        lambda0=lambda0,
        window=300,
        T_threshold=0.1
    )

    print("\n=== FINAL METRICS (Physics-Verified) ===")
    print(m)

    # 6) Render neat schematic from updated JSON
    updated_cfg = load_design(str(updated_json_path))
    img_path = render_stack(updated_cfg, out_name="bragg_stack.png")
    print("\nSaved schematic:", img_path)

    print("\n✅ DONE: JSON → Bayesian Optimization → TMM validation → Updated JSON → Schematic")


if __name__ == "__main__":
    main()