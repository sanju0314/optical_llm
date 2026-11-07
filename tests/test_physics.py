from __future__ import annotations
import numpy as np
from physics.tmm_1d import spectrum

def test_energy_conservation_lossless_stack_normal_incidence():
    lambda0 = 1000.0
    periods = 10
    n1, n2 = 1.45, 2.40
    n_in, n_out = 1.0, 1.0
    d1 = lambda0 / (4.0 * n1)
    d2 = lambda0 / (4.0 * n2)
    n_layers = [n1, n2] * periods
    d_layers = [d1, d2] * periods
    wavelengths = np.linspace(700.0, 1300.0, 51)
    R, T = spectrum(n_in, n_out, n_layers, d_layers, wavelengths)

    # stay in 0 to 1
    assert np.all(R >= -1e-9) and np.all(R <= 1.0 + 1e-6)
    assert np.all(T >= -1e-9) and np.all(T <= 1.0 + 1e-6)
    # Energy conservation
    err = np.max(np.abs((R + T) - 1.0))
    assert err < 1e-4
