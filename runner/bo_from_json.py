from __future__ import annotations

import numpy as np
import optuna

from config.load_design import load_design
from physics.tmm_1d import spectrum
from physics.metrics import bandgap_metrics


def objective_factory(cfg: dict):
    # Read config
    lambda0 = float(cfg["lambda0_nm"])
    wmin, wmax = cfg["wavelength_range_nm"]
    periods = int(cfg["structure"]["periods"])
    order = cfg["structure"].get("order", "HL").upper()

    n_a = float(cfg.get("ambient_n", 1.0))
    n_s = float(cfg.get("substrate_n", 1.0))

    n_low = float(cfg["materials"][0]["n"])
    n_high = float(cfg["materials"][1]["n"])

    # Targets
    max_center_err = float(cfg["targets"]["max_center_error_nm"])
    min_width = float(cfg["targets"]["min_bandgap_width_nm"])
    max_minT = float(cfg["targets"]["max_minT"])

    # Base quarter-wave thicknesses
    d_low_base = lambda0 / (4.0 * n_low)
    d_high_base = lambda0 / (4.0 * n_high)

    # Wavelength sampling
    wavelengths = np.linspace(float(wmin), float(wmax), 801)

    def objective(trial: optuna.Trial) -> float:
        # Bayesian Optimization variables (simple but powerful)
        scale = trial.suggest_float("scale", 0.90, 1.05)
        ratio = trial.suggest_float("ratio", 0.95, 1.05)  # balances low vs high thickness

        d_low = d_low_base * scale * ratio
        d_high = d_high_base * scale / ratio

        # Build layers based on order
        if order == "HL":
            n_layers = [n_high, n_low] * periods
            d_layers = [d_high, d_low] * periods
        else:  # "LH"
            n_layers = [n_low, n_high] * periods
            d_layers = [d_low, d_high] * periods

        R, T = spectrum(n_a, n_s, n_layers, d_layers, wavelengths)
        m = bandgap_metrics(wavelengths, T, lambda0=lambda0, window=300, T_threshold=0.1)

        # Penalize invalid solutions
        if not m.get("has_bandgap", False):
            return 1e6

        center_err = abs(m["center_error_nm"])
        width = m["width_nm"]
        minT = m["min_T"]

        # Penalties enforce research constraints
        penalty = 0.0
        if center_err > max_center_err:
            penalty += 50.0 * (center_err - max_center_err)
        if width < min_width:
            penalty += 5.0 * (min_width - width)
        if minT > max_minT:
            penalty += 5000.0 * (minT - max_minT)

        # Main objective: get center error as low as possible
        return center_err + penalty

    # Return all constants too so we can reconstruct best design
    return objective, {
        "lambda0": lambda0,
        "periods": periods,
        "order": order,
        "n_a": n_a,
        "n_s": n_s,
        "n_low": n_low,
        "n_high": n_high,
        "d_low_base": d_low_base,
        "d_high_base": d_high_base,
        "wavelengths": wavelengths,
    }


def main():
    cfg = load_design()
    method = cfg["optimization"].get("method", "bayesian").lower()
    if method != "bayesian":
        raise ValueError("This runner supports only optimization.method = 'bayesian' for now.")

    trials = int(cfg["optimization"].get("trials", 40))

    objective, const = objective_factory(cfg)

    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=trials)

    best = study.best_params
    scale = best["scale"]
    ratio = best["ratio"]

    d_low = const["d_low_base"] * scale * ratio
    d_high = const["d_high_base"] * scale / ratio

    print("\n=== Best Design (from JSON + BO) ===")
    print("Best params:", best)
    print(f"d_low_nm  = {d_low:.6f}")
    print(f"d_high_nm = {d_high:.6f}")
    print("order =", const["order"])
    print("periods =", const["periods"])

    # Final metrics check
    if const["order"] == "HL":
        n_layers = [const["n_high"], const["n_low"]] * const["periods"]
        d_layers = [d_high, d_low] * const["periods"]
    else:
        n_layers = [const["n_low"], const["n_high"]] * const["periods"]
        d_layers = [d_low, d_high] * const["periods"]

    R, T = spectrum(const["n_a"], const["n_s"], n_layers, d_layers, const["wavelengths"])
    m = bandgap_metrics(const["wavelengths"], T, lambda0=const["lambda0"], window=300, T_threshold=0.1)

    print("\nFinal metrics:", m)


if __name__ == "__main__":
    main()