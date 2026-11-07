from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
from physics.tmm_1d import spectrum
from physics.metrics import bandgap_metrics

def build_bragg_stack(n1: float, n2: float, lambda0: float, periods: int) -> tuple[list[float], list[float]]:
    #Quarter-wave Bragg stack design at lambda0:
     
    d1 = lambda0 / (4.0 * n1)
    d2 = lambda0 / (4.0 * n2)
    scale = 1000.0 / 1029.5  # for tuning purpses
    d1 *= scale
    d2 *= scale
    n_layers: list[float] = []
    d_layers: list[float] = []

    for _ in range(periods):
        n_layers += [n1, n2]
        d_layers += [d1, d2]

    return n_layers, d_layers

def main() -> None:
    # Design target
    lambda0 = 1000.0  # in nanometer
    periods = 10

    # material used: SiO2 and TiO2
    n1 = 1.45
    n2 = 2.40

    # incident & substrate media - air-air
    n_in = 1.0
    n_out = 1.0
    n_layers, d_layers = build_bragg_stack(n1, n2, lambda0, periods)

    wavelengths = np.linspace(600.0, 1400.0, 801)  # nm
    R, T = spectrum(n_in, n_out, n_layers, d_layers, wavelengths)
    # Plot
    plt.figure()
    plt.plot(wavelengths, T, label="Transmission T")
    plt.plot(wavelengths, R, label="Reflectance R")
    plt.axvline(lambda0, linestyle="--", label="lambda0=1000 nm")
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Power")
    plt.title("1D Photonic Crystal (Bragg Stack) Spectrum")
    plt.ylim(0, 1.05)
    plt.grid(True)
    plt.legend()
    plt.show()

    print("At lambda0=1000 nm:")
    idx = np.argmin(np.abs(wavelengths - lambda0))
    print("  T =", T[idx])
    print("  R =", R[idx])
    print("  T+R =", T[idx] + R[idx])
    m = bandgap_metrics(wavelengths, T, lambda0=lambda0, window=300, T_threshold=0.1)
    print("\nBandgap metrics near lambda0:")
    for k, v in m.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
