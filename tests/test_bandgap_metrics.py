from __future__ import annotations
import numpy as np
from physics.tmm_1d import spectrum
from physics.metrics import bandgap_metrics

def test_bragg_stack_has_bandgap_near_1000nm():
    lambda0 = 1000.0
    periods = 10
    n1, n2 = 1.45, 2.40
    n_in, n_out = 1.0, 1.0

    d1 = lambda0 / (4.0 * n1)
    d2 = lambda0 / (4.0 * n2)

    n_layers = [n1, n2] * periods
    d_layers = [d1, d2] * periods

    wavelengths = np.linspace(600.0, 1400.0, 801)
    R, T = spectrum(n_in, n_out, n_layers, d_layers, wavelengths)

    m = bandgap_metrics(wavelengths, T, lambda0=lambda0, window=300, T_threshold=0.1)

    assert m["has_bandgap"] is True
    assert m["min_T"] < 0.2          # deep drop
    assert m["width_nm"] > 100.0     # not too narrow
    assert abs(m["center_error_nm"]) < 80.0  # roughly centered (tolerance)
