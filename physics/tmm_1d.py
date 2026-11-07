from __future__ import annotations
import numpy as np
def _n_cos_theta(n: complex, theta: float) -> complex:
    
    return n * np.cos(theta)

def layer_matrix(n: complex, d: float, wavelength: float) -> np.ndarray:
    
    k0 = 2.0 * np.pi / wavelength
    delta = k0 * n * d  # phase thickness

    # At normal incidence, optical admittance q = n (for non-magnetic materials)
    q = n
    c = np.cos(delta)
    s = 1j * np.sin(delta)
    # 2x2 characteristic matrix
    M = np.array([[c, s / q],
                  [s * q, c]], dtype=complex)
    return M

def stack_matrix(n_list: list[complex], d_list: list[float], wavelength: float) -> np.ndarray:
    
    if len(n_list) != len(d_list):
        raise ValueError("n_list and d_list must have same length")

    Mtot = np.eye(2, dtype=complex)
    for n, d in zip(n_list, d_list):
        Mtot = Mtot @ layer_matrix(n, d, wavelength)
    return Mtot

def reflect_transmit(
    n_in: complex,
    n_out: complex,
    n_layers: list[complex],
    d_layers: list[float],
    wavelength: float,
) -> tuple[float, float]:
    #Compute Reflectance R and Transmittance T at NORMAL incidence
    M = stack_matrix(n_layers, d_layers, wavelength)
    # Admittances at normal incidence
    q0 = n_in
    qs = n_out

    A, B = M[0, 0], M[0, 1]
    C, D = M[1, 0], M[1, 1]

    # amplitude reflection & transmission (standard characteristic matrix formula)
    denom = (q0 * A + q0 * qs * B + C + qs * D)
    r = (q0 * A + q0 * qs * B - C - qs * D) / denom
    t = (2.0 * q0) / denom
    R = float(np.real(r * np.conj(r)))
    # Power transmittance scaling (normal incidence): T = (Re(qs)/Re(q0)) * |t|^2
    T = float((np.real(qs) / np.real(q0)) * np.real(t * np.conj(t)))
    return R, T

def spectrum(
    n_in: complex,
    n_out: complex,
    n_layers: list[complex],
    d_layers: list[float],
    wavelengths: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    R = np.zeros_like(wavelengths, dtype=float)
    T = np.zeros_like(wavelengths, dtype=float)

    for i, wl in enumerate(wavelengths):
        Ri, Ti = reflect_transmit(n_in, n_out, n_layers, d_layers, float(wl))
        R[i] = Ri
        T[i] = Ti
    return R, T
