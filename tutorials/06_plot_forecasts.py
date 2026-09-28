#!/usr/bin/env python3
"""
Plot LeR population forecasts from ``ler_data/`` into ``forecasts/`` as PDFs.

For each quantity, three PDFs are written:

- ``sl_intrinsic_*`` — strongly lensed parent population (SL-conditioned, pre-detection)
- ``detectable_*`` — detectable subsample
- ``comparison_*`` — SL-intrinsic and detectable overlaid / side-by-side

Note: ``lensed_param.json`` is already conditioned on strong lensing (optical depth /
multi-image selection). Unlensed samples are not SL-conditioned.

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

# Reference time-delay markers on the log-|Δt| axis (values in days).
TIME_DELAY_MARKERS = (
    (SEC_TO_DAY, "second"),
    (60.0 * SEC_TO_DAY, "minute"),
    (3600.0 * SEC_TO_DAY, "hour"),
    (1.0, "day"),
    (30.0, "month"),
    (365.25, "year"),
)


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
    values = dt[:, 1:].ravel()
    values = values[np.isfinite(values) & (values != 0.0)]
    return np.abs(values) * SEC_TO_DAY


def _sigma_zl(lensed: dict) -> tuple[np.ndarray, np.ndarray]:
    return (
        np.asarray(lensed["zl"], dtype=float),
        np.asarray(lensed["sigma"], dtype=float),
    )


def _theta_e(lensed: dict) -> np.ndarray:
    return einstein_radius_arcsec(
        np.asarray(lensed["sigma"], dtype=float),
        np.asarray(lensed["zl"], dtype=float),
        np.asarray(lensed["zs"], dtype=float),
    )


def _save(fig: plt.Figure, name: str) -> Path:
    out = FORECASTS / name
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    return out


def _plot_source_redshift_curves(curves: list[tuple[Path, str, float | None]]) -> plt.Figure:
    apply_corner_style()
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    plt.sca(ax)
    for path, label, bandwidth in curves:
        kwargs = dict(
            param_name="zs",
            param_dict=str(path),
            plot_label=label,
            histogram=False,
            kde=True,
        )
        if bandwidth is not None:
            kwargs["kde_bandwidth"] = bandwidth
        lerplt.param_plot(**kwargs)
    ax.set_xlim(0.0, 8.0)
    ax.set_xlabel(r"Source redshift $z_\mathrm{s}$")
    ax.set_ylabel("Probability density")
    ax.grid(alpha=0.4)
    return fig


def plot_source_redshifts() -> list[Path]:
    sl_intrinsic = _plot_source_redshift_curves(
        [
            (UNLENSED_ALL, "unlensed", None),
            (LENSED_ALL, "lensed (SL intrinsic)", None),
        ]
    )
    detectable = _plot_source_redshift_curves(
        [
            (UNLENSED_DET, "unlensed", 0.5),
            (LENSED_DET, "lensed (detectable)", 0.5),
        ]
    )
    comparison = _plot_source_redshift_curves(
        [
            (UNLENSED_ALL, "unlensed (all)", None),
            (UNLENSED_DET, "unlensed (detectable)", 0.5),
            (LENSED_ALL, "lensed (SL intrinsic)", None),
            (LENSED_DET, "lensed (detectable)", 0.5),
        ]
    )
    return [
        _save(sl_intrinsic, "sl_intrinsic_source_redshift.pdf"),
        _save(detectable, "detectable_source_redshift.pdf"),
        _save(comparison, "comparison_source_redshift.pdf"),
    ]


def _plot_sigma_zl_hexbin(
    lensed: dict,
    *,
    gridsize: int,
    title: str | None = None,
) -> plt.Figure:
    apply_corner_style()
    zl, sigma = _sigma_zl(lensed)
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    hb = ax.hexbin(zl, sigma, gridsize=gridsize, cmap="viridis", mincnt=1, bins="log")
    cb = fig.colorbar(hb, ax=ax)
    cb.set_label(r"$\log_{10} N$")
    if title:
        ax.set_title(title)
    ax.set_xlabel(r"Lens redshift $z_\mathrm{l}$")
    ax.set_ylabel(r"Velocity dispersion $\sigma$ [km s$^{-1}$]")
    ax.grid(alpha=0.3)
    return fig


def plot_velocity_dispersion_vs_redshift(lensed_all: dict, lensed_det: dict) -> list[Path]:
    sl_intrinsic = _plot_sigma_zl_hexbin(lensed_all, gridsize=60)
    detectable = _plot_sigma_zl_hexbin(lensed_det, gridsize=25)

    apply_corner_style()
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), sharex=True, sharey=True)
    for ax, label, sample, gridsize in (
        (axes[0], "SL intrinsic", lensed_all, 60),
        (axes[1], "detectable", lensed_det, 25),
    ):
        zl, sigma = _sigma_zl(sample)
        hb = ax.hexbin(zl, sigma, gridsize=gridsize, cmap="viridis", mincnt=1, bins="log")
        cb = fig.colorbar(hb, ax=ax)
        cb.set_label(r"$\log_{10} N$")
        ax.set_title(label)
        ax.set_xlabel(r"Lens redshift $z_\mathrm{l}$")
        ax.grid(alpha=0.3)
    axes[0].set_ylabel(r"Velocity dispersion $\sigma$ [km s$^{-1}$]")

    return [
        _save(sl_intrinsic, "sl_intrinsic_velocity_dispersion_vs_redshift.pdf"),
        _save(detectable, "detectable_velocity_dispersion_vs_redshift.pdf"),
        _save(fig, "comparison_velocity_dispersion_vs_redshift.pdf"),
    ]


def _plot_einstein_hist(
    samples: list[tuple[np.ndarray, str, str]],
    bins: np.ndarray,
) -> plt.Figure:
    apply_corner_style()
    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    for values, label, color in samples:
        ax.hist(values, bins=bins, density=True, histtype="step", color=color, label=label)
    ax.set_xlabel(r"Einstein radius $\theta_\mathrm{E}$ [arcsec]")
    ax.set_ylabel("Probability density")
    ax.legend(frameon=False)
    ax.grid(alpha=0.4)
    return fig


def plot_einstein_radii(lensed_all: dict, lensed_det: dict) -> list[Path]:
    theta_all = _theta_e(lensed_all)
    theta_det = _theta_e(lensed_det)
    bins = np.linspace(
        min(theta_all.min(), theta_det.min()),
        max(theta_all.max(), theta_det.max()),
        60,
    )
    return [
        _save(
            _plot_einstein_hist([(theta_all, "SL intrinsic", "C0")], bins),
            "sl_intrinsic_einstein_radius.pdf",
        ),
        _save(
            _plot_einstein_hist([(theta_det, "detectable", "C1")], bins),
            "detectable_einstein_radius.pdf",
        ),
        _save(
            _plot_einstein_hist(
                [
                    (theta_all, "SL intrinsic", "C0"),
                    (theta_det, "detectable", "C1"),
                ],
                bins,
            ),
            "comparison_einstein_radius.pdf",
        ),
    ]


def _plot_time_delay_hist(
    samples: list[tuple[np.ndarray, str, str]],
    bins: np.ndarray,
) -> plt.Figure:
    apply_corner_style()
    fig, ax = plt.subplots(figsize=(6.5, 4.0))
    for values, label, color in samples:
        ax.hist(values, bins=bins, density=True, histtype="step", color=color, label=label)
    ax.set_xscale("log")
    ax.set_xlabel(r"Image time delay $|\Delta t|$ [days]")
    ax.set_ylabel("Probability density")

    data_min = min(float(values.min()) for values, _, _ in samples)
    data_max = max(float(values.max()) for values, _, _ in samples)
    ax.set_xlim(
        min(data_min, TIME_DELAY_MARKERS[0][0]) * 0.7,
        max(data_max, TIME_DELAY_MARKERS[-1][0]) * 1.3,
    )

    for x_days, name in TIME_DELAY_MARKERS:
        ax.axvline(x_days, color="0.55", ls=":", lw=0.9, zorder=0)
        ax.text(
            x_days,
            0.98,
            name,
            transform=ax.get_xaxis_transform(),
            rotation=90,
            va="top",
            ha="right",
            fontsize=8,
            color="0.35",
        )
    ax.legend(frameon=False)
    ax.grid(alpha=0.4, which="both")
    return fig


def plot_time_delays(lensed_all: dict, lensed_det: dict) -> list[Path]:
    dt_all = image_time_delays_days(lensed_all["time_delays"])
    dt_det = image_time_delays_days(lensed_det["time_delays"])
    positive_all = dt_all[dt_all > 0.0]
    positive_det = dt_det[dt_det > 0.0]
    lo = min(positive_all.min(), positive_det.min())
    hi = max(positive_all.max(), positive_det.max())
    bins = np.logspace(np.log10(lo), np.log10(hi), 60)
    return [
        _save(
            _plot_time_delay_hist([(positive_all, "SL intrinsic", "C0")], bins),
            "sl_intrinsic_time_delays.pdf",
        ),
        _save(
            _plot_time_delay_hist([(positive_det, "detectable", "C1")], bins),
            "detectable_time_delays.pdf",
        ),
        _save(
            _plot_time_delay_hist(
                [
                    (positive_all, "SL intrinsic", "C0"),
                    (positive_det, "detectable", "C1"),
                ],
                bins,
            ),
            "comparison_time_delays.pdf",
        ),
    ]


def main() -> None:
    for path in (UNLENSED_ALL, UNLENSED_DET, LENSED_ALL):
        if not path.exists():
            raise FileNotFoundError(f"Missing {path}; run 05_ler.py before plotting.")

    ensure_lensed_detectable()
    FORECASTS.mkdir(parents=True, exist_ok=True)

    # Drop legacy PDF names from earlier versions of this script.
    for legacy in FORECASTS.glob("intrinsic_*.pdf"):
        legacy.unlink()
    for legacy in (
        "source_redshift.pdf",
        "velocity_dispersion_vs_redshift.pdf",
        "einstein_radius.pdf",
        "time_delays.pdf",
    ):
        legacy_path = FORECASTS / legacy
        if legacy_path.exists():
            legacy_path.unlink()

    lensed_all = get_param_from_json(str(LENSED_ALL))
    lensed_det = get_param_from_json(str(LENSED_DET))

    outputs: list[Path] = []
    outputs.extend(plot_source_redshifts())
    outputs.extend(plot_velocity_dispersion_vs_redshift(lensed_all, lensed_det))
    outputs.extend(plot_einstein_radii(lensed_all, lensed_det))
    outputs.extend(plot_time_delays(lensed_all, lensed_det))

    print("Wrote forecasts:")
    for path in outputs:
        print(f"  {path}")


if __name__ == "__main__":
    main()
