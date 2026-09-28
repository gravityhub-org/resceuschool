"""Shared matplotlib / corner styling for tutorial posterior plots."""

from __future__ import annotations

import matplotlib.pyplot as plt

# Imported for side effect: registers the "science" style with matplotlib.
import scienceplots  # noqa: F401

# Common kwargs for corner.corner (fonts sized for scienceplots + larger labels).
CORNER_KWARGS = dict(
    quantiles=[0.16, 0.5, 0.84],
    show_titles=True,
    title_fmt=".4g",
    title_kwargs={"fontsize": 14},
    label_kwargs={"fontsize": 16},
    bins=28,
    smooth=1.0,
    levels=(0.5, 0.9),
    plot_datapoints=False,
    fill_contours=True,
    max_n_ticks=4,
)


def apply_corner_style() -> None:
    """SciencePlots style with larger fonts for corner plots."""
    plt.style.use(["science", "no-latex"])
    plt.rcParams.update(
        {
            "font.size": 14,
            "axes.labelsize": 16,
            "axes.titlesize": 16,
            "xtick.labelsize": 12,
            "ytick.labelsize": 12,
            "legend.fontsize": 12,
            "figure.titlesize": 16,
        }
    )
