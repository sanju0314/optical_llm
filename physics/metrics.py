from __future__ import annotations
import numpy as np

def bandgap_metrics(
    wavelengths: np.ndarray,
    T: np.ndarray,
    lambda0: float,
    window: float = 300.0,
    T_threshold: float = 0.1,
) -> dict:
    w = wavelengths
    T = np.asarray(T)
    mask = (w >= lambda0 - window) & (w <= lambda0 + window)
    if np.sum(mask) < 5:
        return {"has_bandgap": False}

    w2 = w[mask]
    T2 = T[mask]
    min_T = float(np.min(T2))
    # bandgap region where transmission is low
    low = T2 <= T_threshold
    if not np.any(low):
        return {
            "has_bandgap": False,
            "min_T": min_T,
        }
    # Find the largest continuous low-transmission segment
    idx = np.where(low)[0]
    # Split into contiguous segments
    splits = np.where(np.diff(idx) > 1)[0] + 1
    segments = np.split(idx, splits)
    # pick longest segment
    seg = max(segments, key=len)

    left = float(w2[seg[0]])
    right = float(w2[seg[-1]])
    width = right - left
    center = 0.5 * (left + right)

    return {
        "has_bandgap": True,
        "min_T": min_T,
        "left_edge_nm": left,
        "right_edge_nm": right,
        "width_nm": float(width),
        "center_nm": float(center),
        "center_error_nm": float(center - lambda0),
    }
