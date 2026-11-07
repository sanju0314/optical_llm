from __future__ import annotations


def pass_criteria(metrics: dict) -> tuple[bool, str]:
    """
    Decide whether a design is acceptable based on bandgap metrics.
    """
    if not metrics.get("has_bandgap", False):
        return False, "FAIL: No bandgap detected near target."

    if metrics.get("min_T", 1.0) > 0.2:
        return False, f"FAIL: Bandgap too shallow (min_T={metrics['min_T']:.3f})."

    if metrics.get("width_nm", 0.0) < 100.0:
        return False, f"FAIL: Bandgap too narrow (width_nm={metrics['width_nm']:.1f} nm)."

    if abs(metrics.get("center_error_nm", 1e9)) > 20.0:
        return False, f"FAIL: Center error too high (center_error_nm={metrics['center_error_nm']:.1f} nm)."

    return True, "PASS"