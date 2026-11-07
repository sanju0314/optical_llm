from __future__ import annotations
import numpy as np

from physics.tmm_1d import spectrum
from physics.metrics import bandgap_metrics


def evaluate_design(d1: float, d2: float, *, n1=1.45, n2=2.40, periods=10, lambda0=1000.0) -> dict:
    n_layers = [n1, n2] * periods
    d_layers = [d1, d2] * periods
    wavelengths = np.linspace(600.0, 1400.0, 801)
    R, T = spectrum(1.0, 1.0, n_layers, d_layers, wavelengths)
    return bandgap_metrics(wavelengths, T, lambda0=lambda0, window=300, T_threshold=0.1)


def auto_tune_scale(*, n1=1.45, n2=2.40, lambda0=1000.0, periods=10, iters=5):
    # quarter-wave initial
    d1 = lambda0 / (4.0 * n1)
    d2 = lambda0 / (4.0 * n2)

    scale = 1.0

    for k in range(iters):
        m = evaluate_design(d1 * scale, d2 * scale, n1=n1, n2=n2, periods=periods, lambda0=lambda0)
        if not m.get("has_bandgap", False):
            return {"ok": False, "reason": "No bandgap detected", "scale": scale, "metrics": m}

        center = m["center_nm"]
        err = m["center_error_nm"]
        print(f"Iter {k}: scale={scale:.6f}, center={center:.2f}, err={err:+.2f}")

        if abs(err) <= 5.0:
            return {"ok": True, "scale": scale, "d1": d1 * scale, "d2": d2 * scale, "metrics": m}

        # Update scale to push center towards lambda0
        scale *= (lambda0 / center)

    # final report
    m = evaluate_design(d1 * scale, d2 * scale, n1=n1, n2=n2, periods=periods, lambda0=lambda0)
    return {"ok": abs(m.get("center_error_nm", 1e9)) <= 5.0, "scale": scale, "d1": d1 * scale, "d2": d2 * scale, "metrics": m}


if __name__ == "__main__":
    result = auto_tune_scale()
    print("\nFinal:")
    print(" ok:", result["ok"])
    print(" d1:", result.get("d1"))
    print(" d2:", result.get("d2"))
    print(" metrics:", result.get("metrics"))