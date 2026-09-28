#!/usr/bin/env python3
"""
Plot LeR population forecasts from ``ler_data/`` into ``forecasts/`` as PDFs.

Requires ``05_ler.py`` to have produced the unlensed/lensed parameter JSONs.
If ``lensed_param_detectable.json`` is missing, it is regenerated via ``LeR.lensed_rate``.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from astropy.cosmology import LambdaCDM

from ler.utils import get_param_from_json
from ler.utils import plots as lerplt
from plot_style import apply_corner_style

ROOT = Path(__file__).resolve().parent
LER_DATA = ROOT / "ler_data"
FORECASTS = ROOT / "forecasts"

UNLENSED_ALL = LER_DATA / "unlensed_param.json"
UNLENSED_DET = LER_DATA / "unlensed_param_detectable.json"
LENSED_ALL = LER_DATA / "lensed_param.json"
LENSED_DET = LER_DATA / "lensed_param_detectable.json"

COSMO = LambdaCDM(H0=70.0, Om0=0.3, Ode0=0.7, Tcmb0=0.0, Neff=3.04, m_nu=None, Ob0=0.0)
C_KMS = 299792.458
RAD_TO_ARCSEC = 180.0 * 3600.0 / np.pi
SEC_TO_DAY = 1.0 / (24.0 * 3600.0)


def ensure_lensed_detectable() -> None:
    """Create detectable lensed JSON if ``05_ler.py`` has not done so yet."""
    if LENSED_DET.exists():
        return
    if not LENSED_ALL.exists():
        raise FileNotFoundError(
            f"Missing {LENSED_ALL}; run 05_ler.py before plotting forecasts."
        )
    from ler.rates import LeR

    print(f"{LENSED_DET.name} missing; computing lensed detectable sample…")
    ler = LeR(npool=6, verbose=False)
    ler.lensed_rate()


def einstein_radius_arcsec(sigma: np.ndarray, zl: np.ndarray, zs: np.ndarray) -> np.ndarray:
    """SIS Einstein radius in arcseconds from σ [km/s] and redshifts."""
    ds = COSMO.angular_diameter_distance(zs).value
    dls = COSMO.angular_diameter_distance_z1z2(zl, zs).value
    theta_e_rad = 4.0 * np.pi * (sigma / C_KMS) ** 2 * dls / ds
    return theta_e_rad * RAD_TO_ARCSEC


def image_time_delays_days(time_delays) -> np.ndarray:
    """Absolute image time delays relative to the first image, in days."""
    dt = np.asarray(time_delays, dtype=float)
    if dt.ndim == 1:
        return np.array([], dtype=float)
    # First column is the reference image (delay 0); later columns may be NaN.
    values = dt[:, 1:].ravel()
    values = values[np.isfinite(values) & (values != 0.0)]
    return np.abs(values) * SEC_TO_DAY


def plot_source_redshifts() -> Path:
    out = FORECASTS / "source_redshift.pdf"
    apply_corner_style()
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    plt.sca(ax)

    lerplt.param_plot(
        param_name="zs",
        param_dict=str(UNLENSED_ALL),
        plot_label="unlensed (all)",
        histogram=False,
        kde=True,
    )
    lerplt.param_plot(
        param_name="zs",
        param_dict=str(UNLENSED_DET),
        plot_label="unlensed (detectable)",
        histogram=False,
        kde=True,
        kde_bandwidth=0.5,
    )
    lerplt.param_plot(
        param_name="zs",
        param_dict=str(LENSED_ALL),
        plot_label="lensed (all)",
        histogram=False,
        kde=True,
    )
    lerplt.param_plot(
        param_name="zs",
        param_dict=str(LENSED_DET),
        plot_label="lensed (detectable)",
        histogram=False,
        kde=True,
        kde_bandwidth=0.5,
    )

    ax.set_xlim(0.0, 8.0)
    ax.set_xlabel(r"Source redshift $z_\mathrm{s}$")
    ax.set_ylabel("Probability density")
    ax.grid(alpha=0.4)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    return out


def plot_velocity_dispersion_vs_redshift(lensed: dict) -> Path:
    out = FORECASTS / "velocity_dispersion_vs_redshift.pdf"
    apply_corner_style()
    zl = np.asarray(lensed["zl"], dtype=float)
    sigma = np.asarray(lensed["sigma"], dtype=float)

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    hb = ax.hexbin(zl, sigma, gridsize=60, cmap="viridis", mincnt=1, bins="log")
    cb = fig.colorbar(hb, ax=ax)
    cb.set_label(r"$\log_{10} N$")
    ax.set_xlabel(r"Lens redshift $z_\mathrm{l}$")
    ax.set_ylabel(r"Velocity dispersion $\sigma$ [km s$^{-1}$]")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    return out


def plot_einstein_radii(lensed: dict) -> Path:
    out = FORECASTS / "einstein_radius.pdf"
    apply_corner_style()
    theta_e = einstein_radius_arcsec(
        np.asarray(lensed["sigma"], dtype=float),
        np.asarray(lensed["zl"], dtype=float),
        np.asarray(lensed["zs"], dtype=float),
    )

    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    ax.hist(theta_e, bins=60, density=True, histtype="step", color="C0", label="all lensed")
    ax.set_xlabel(r"Einstein radius $\theta_\mathrm{E}$ [arcsec]")
    ax.set_ylabel("Probability density")
    ax.legend(frameon=False)
    ax.grid(alpha=0.4)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    return out


def plot_time_delays(lensed: dict) -> Path:
    out = FORECASTS / "time_delays.pdf"
    apply_corner_style()
    dt_days = image_time_delays_days(lensed["time_delays"])
    # Log-spaced bins cover the broad delay distribution.
    positive = dt_days[dt_days > 0.0]
    bins = np.logspace(np.log10(positive.min()), np.log10(positive.max()), 60)

    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    ax.hist(positive, bins=bins, density=True, histtype="step", color="C1", label="all lensed")
    ax.set_xscale("log")
    ax.set_xlabel(r"Image time delay $|\Delta t|$ [days]")
    ax.set_ylabel("Probability density")
    ax.legend(frameon=False)
    ax.grid(alpha=0.4, which="both")
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    return out


def main() -> None:
    for path in (UNLENSED_ALL, UNLENSED_DET, LENSED_ALL):
        if not path.exists():
            raise FileNotFoundError(f"Missing {path}; run 05_ler.py before plotting.")

    ensure_lensed_detectable()
    FORECASTS.mkdir(parents=True, exist_ok=True)

    lensed = get_param_from_json(str(LENSED_ALL))

    outputs = [
        plot_source_redshifts(),
        plot_velocity_dispersion_vs_redshift(lensed),
        plot_einstein_radii(lensed),
        plot_time_delays(lensed),
    ]
    print("Wrote forecasts:")
    for path in outputs:
        print(f"  {path}")


if __name__ == "__main__":
    main()
