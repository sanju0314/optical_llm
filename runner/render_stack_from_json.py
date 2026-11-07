from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from config.load_design import load_design


def render_stack(cfg: dict, *, out_name: str = "bragg_stack.png") -> Path:
    """
    Render a neat 1D Bragg stack lattice diagram (like a circuit-style schematic)
    using values from cfg (design_input.json).

    Convention:
      materials[0] = low index (L)
      materials[1] = high index (H)
      structure.d1_nm = low thickness (L)
      structure.d2_nm = high thickness (H)
    """
    lambda0 = float(cfg["lambda0_nm"])
    periods = int(cfg["structure"]["periods"])
    order = str(cfg["structure"].get("order", "HL")).upper()

    low = cfg["materials"][0]
    high = cfg["materials"][1]
    nameL, nL = str(low["name"]), float(low["n"])
    nameH, nH = str(high["name"]), float(high["n"])

    d1 = cfg["structure"].get("d1_nm", None)  # low thickness
    d2 = cfg["structure"].get("d2_nm", None)  # high thickness

    # If not yet optimized, default to quarter-wave
    if d1 is None:
        d1 = lambda0 / (4.0 * nL)
    if d2 is None:
        d2 = lambda0 / (4.0 * nH)

    dL = float(d1)
    dH = float(d2)

    # Build layer sequence by order
    if order == "HL":
        layers = [(nameH, nH, dH), (nameL, nL, dL)] * periods
    elif order == "LH":
        layers = [(nameL, nL, dL), (nameH, nH, dH)] * periods
    else:
        raise ValueError("structure.order must be 'HL' or 'LH'")

    total_thickness = sum(d for _, _, d in layers)

    fig, ax = plt.subplots(figsize=(7, 10))
    y = 0.0

    # Draw rectangles stacked in Y direction
    for idx, (mat, n, d) in enumerate(layers, start=1):
        rect = Rectangle((0.0, y), 1.0, d, fill=False, linewidth=1.5)
        ax.add_patch(rect)
        ax.text(
            0.5,
            y + d / 2,
            f"{idx:02d}  {mat}  (n={n:.3f})\n d={d:.2f} nm",
            ha="center",
            va="center",
            fontsize=9,
        )
        y += d

    ax.set_xlim(0, 1)
    ax.set_ylim(0, total_thickness)
    ax.set_xticks([])
    ax.set_ylabel("Thickness (nm)")
    ax.set_title(
        f"1D Bragg Stack (λ0={lambda0:.0f} nm, periods={periods}, order={order})"
    )

    # Put first layer at top visually
    ax.invert_yaxis()
    plt.tight_layout()

    project_root = Path(__file__).resolve().parents[1]  # optillm/
    out_path = project_root / out_name
    fig.savefig(out_path, dpi=300)
    plt.close(fig)

    return out_path


def main():
    cfg = load_design()
    out = render_stack(cfg, out_name="bragg_stack.png")
    print("Saved schematic:", out)


if __name__ == "__main__":
    main()