#!/usr/bin/env python3
"""Laplace approximation: still PDF + stepped GIF (analytical 1D and 2D).

Pedagogical steps (no trial σ):
  1. Fit MAP
  2. Compute derivatives (Hessian of log-posterior at the MAP)
  3. Invert → σ² = (−H)⁻¹ and draw the Laplace Gaussian
"""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")

import imageio.v2 as imageio
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from scipy import stats

import scienceplots  # noqa: F401

plt.style.use(["science", "no-latex"])

C_TRUE = "#0072B2"
C_LAPLACE = "#E69F00"
C_MAP = "#000000"
C_HESS = "#009E73"

FIGDIR = Path(__file__).resolve().parents[1]
OUT_PDF = FIGDIR / "laplace_approximation.pdf"
OUT_GIF = FIGDIR / "laplace_approximation.gif"

K1D = 4.0
KX, KY = 4.0, 5.0
XMAX_1D = 10.0
XMAX_2D, YMAX_2D = 8.5, 10.0
FRAC_LEVELS = np.array([0.20, 0.45, 0.75])


def gamma_laplace(k: float, scale: float = 1.0) -> tuple[float, float, float]:
    """MAP, Laplace σ, and Hessian H = ∂² log p / ∂θ² at the MAP (unit-scale Gamma)."""
    mode = (k - 1.0) * scale
    # log p = (k-1) log θ − θ/scale + … → H = −(k-1)/mode² = −1/((k-1) scale²)
    hess = -1.0 / ((k - 1.0) * scale**2)
    sigma = np.sqrt(-1.0 / hess)  # σ² = (−H)⁻¹
    return mode, sigma, hess


def _fig_to_rgb(fig: plt.Figure) -> np.ndarray:
    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())
    return buf[:, :, :3].copy()


def _style_axes(ax1: plt.Axes, ax2: plt.Axes, y1_max: float) -> None:
    ax1.set_xlim(0.0, XMAX_1D)
    ax1.set_ylim(0.0, y1_max)
    ax1.set_xlabel(r"Parameter $\theta$")
    ax1.set_ylabel(r"$p(\theta\,|\,d)$")
    ax1.set_title("1D")

    ax2.set_xlim(0.0, XMAX_2D)
    ax2.set_ylim(0.0, YMAX_2D)
    ax2.set_aspect("equal", adjustable="box")
    ax2.set_xlabel(r"$\theta_1$")
    ax2.set_ylabel(r"$\theta_2$")
    ax2.set_title("2D")


def _step_badge(fig: plt.Figure, text: str) -> None:
    """Discrete step label (not a running σ animation)."""
    fig.text(
        0.5,
        1.01,
        text,
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold",
        transform=fig.transFigure,
    )


def make_panel(step: int) -> plt.Figure:
    """step: 1 = MAP, 2 = derivatives, 3 = invert → Laplace."""
    mode_1d, sigma_1d, hess_1d = gamma_laplace(K1D)
    mode_x, sigma_x, hess_x = gamma_laplace(KX)
    mode_y, sigma_y, hess_y = gamma_laplace(KY)

    x = np.linspace(0.05, 12.0, 600)
    true_1d = stats.gamma.pdf(x, a=K1D, scale=1.0)
    peak_1d = float(stats.gamma.pdf(mode_1d, a=K1D, scale=1.0))
    y1_max = 1.15 * peak_1d

    nx = ny = 240
    X, Y = np.meshgrid(
        np.linspace(0.05, XMAX_2D, nx),
        np.linspace(0.05, YMAX_2D, ny),
        indexing="xy",
    )
    true_2d = stats.gamma.pdf(X, a=KX, scale=1.0) * stats.gamma.pdf(
        Y, a=KY, scale=1.0
    )
    levels_true = FRAC_LEVELS * true_2d.max()

    # Peak-matched Laplace (same MAP height) — σ from (−H)⁻¹ only
    lap_1d = peak_1d * np.exp(-0.5 * ((x - mode_1d) / sigma_1d) ** 2)
    lap_2d = np.exp(
        -0.5 * (((X - mode_x) / sigma_x) ** 2 + ((Y - mode_y) / sigma_y) ** 2)
    )
    levels_lap = FRAC_LEVELS * lap_2d.max()

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(7.4, 3.2), gridspec_kw={"wspace": 0.30}
    )

    # Always: true posterior
    ax1.plot(x, true_1d, color=C_TRUE, lw=2.0, zorder=2)
    ax2.contour(
        X, Y, true_2d, levels=levels_true, colors=C_TRUE, linewidths=1.6, zorder=2
    )
    handles = [
        Line2D([0], [0], color=C_TRUE, lw=2.0, label="True posterior"),
    ]

    # Step ≥1: MAP
    if step >= 1:
        ax1.axvline(mode_1d, color=C_MAP, lw=0.9, ls=":", alpha=0.7, zorder=1)
        ax1.plot(mode_1d, peak_1d, "o", color=C_MAP, ms=6, zorder=5)
        ax2.plot(mode_x, mode_y, "o", color=C_MAP, ms=6, zorder=5)
        handles.append(
            Line2D(
                [0],
                [0],
                marker="o",
                color="none",
                markerfacecolor=C_MAP,
                markeredgecolor=C_MAP,
                markersize=6,
                label=r"MAP $\theta^\star$",
            )
        )
        if step == 1:
            ax1.annotate(
                r"$\theta^\star=\mathrm{argmax}\,p$",
                xy=(mode_1d, peak_1d),
                xytext=(mode_1d + 1.4, peak_1d * 0.72),
                fontsize=8,
                color=C_MAP,
                arrowprops=dict(arrowstyle="->", color=C_MAP, lw=0.8),
            )

    # Step 2: Hessian / second derivatives at the MAP (local quadratic of log p)
    if step == 2:
        half = 1.25 * sigma_1d
        xc = np.linspace(mode_1d - half, mode_1d + half, 250)
        # Taylor: log p ≈ log p★ + ½ H (θ−θ★)²  →  p ≈ p★ exp(½ H (θ−θ★)²)
        local = peak_1d * np.exp(0.5 * hess_1d * (xc - mode_1d) ** 2)
        ax1.plot(xc, local, color=C_HESS, lw=2.0, ls="--", zorder=3)
        ax1.text(
            0.97,
            0.55,
            r"$H=\partial^2_\theta\log p\,|_{\theta^\star}$"
            "\n"
            r"$H=" + f"{hess_1d:.2f}$",
            transform=ax1.transAxes,
            ha="right",
            va="top",
            fontsize=8,
            color=C_HESS,
            bbox=dict(
                boxstyle="round,pad=0.25", facecolor="white", edgecolor=C_HESS, lw=0.8
            ),
        )
        # 2D: local Hessian quadratic as green dashed contours
        ax2.contour(
            X,
            Y,
            lap_2d,
            levels=levels_lap,
            colors=C_HESS,
            linewidths=1.6,
            linestyles="--",
            zorder=3,
        )
        ax2.text(
            0.97,
            0.97,
            r"$H=\nabla\nabla\log p\,|_{\theta^\star}$",
            transform=ax2.transAxes,
            ha="right",
            va="top",
            fontsize=8,
            color=C_HESS,
            bbox=dict(
                boxstyle="round,pad=0.25", facecolor="white", edgecolor=C_HESS, lw=0.8
            ),
        )
        handles.append(
            Line2D([0], [0], color=C_HESS, lw=2.0, ls="--", label="Hessian (local)")
        )

    # Step 3: invert Hessian → covariance, draw Laplace Gaussian
    if step >= 3:
        ax1.plot(x, lap_1d, color=C_LAPLACE, lw=2.0, ls="--", zorder=3)
        ax1.text(
            0.97,
            0.55,
            r"$\sigma^2=(-H)^{-1}$"
            "\n"
            rf"$\sigma={sigma_1d:.2f}$",
            transform=ax1.transAxes,
            ha="right",
            va="top",
            fontsize=8,
            color=C_LAPLACE,
            bbox=dict(
                boxstyle="round,pad=0.25",
                facecolor="white",
                edgecolor=C_LAPLACE,
                lw=0.8,
            ),
        )
        ax2.contour(
            X,
            Y,
            lap_2d,
            levels=levels_lap,
            colors=C_LAPLACE,
            linewidths=1.6,
            linestyles="--",
            zorder=3,
        )
        ax2.text(
            0.97,
            0.97,
            r"$\Sigma=(-H)^{-1}$",
            transform=ax2.transAxes,
            ha="right",
            va="top",
            fontsize=8,
            color=C_LAPLACE,
            bbox=dict(
                boxstyle="round,pad=0.25",
                facecolor="white",
                edgecolor=C_LAPLACE,
                lw=0.8,
            ),
        )
        handles.append(
            Line2D(
                [0], [0], color=C_LAPLACE, lw=2.0, ls="--", label="Laplace approx."
            )
        )

    _style_axes(ax1, ax2, y1_max)
    ax1.legend(handles=handles, loc="upper right", frameon=False, fontsize=8)
    ax2.legend(handles=handles, loc="upper left", frameon=False, fontsize=8)

    labels = {
        1: r"Step 1: fit MAP  $\theta^\star=\mathrm{argmax}\,p(\theta|d)$",
        2: r"Step 2: compute derivatives  $H=\nabla\nabla\log p\,|_{\theta^\star}$",
        3: r"Step 3: invert  $\Sigma=(-H)^{-1}$  (Laplace Gaussian)",
    }
    _step_badge(fig, labels[step])
    return fig


def main() -> None:
    # Final still = step 3
    fig = make_panel(3)
    fig.savefig(OUT_PDF, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {OUT_PDF}")

    # One frame per pedagogical step; long dwell (no trial-σ morphing).
    frames: list[np.ndarray] = []
    durations: list[float] = []
    dwell = 2.0  # seconds per step
    for step in (1, 2, 3):
        fig = make_panel(step)
        frames.append(_fig_to_rgb(fig))
        plt.close(fig)
        durations.append(dwell if step < 3 else dwell * 1.4)

    imageio.mimsave(OUT_GIF, frames, duration=durations, loop=0)
    print(f"wrote {OUT_GIF} ({len(frames)} steps)")


if __name__ == "__main__":
    main()
