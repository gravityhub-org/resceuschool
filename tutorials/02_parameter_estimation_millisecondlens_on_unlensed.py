#!/usr/bin/env python3
"""
Millilensing PE on the *unlensed* LHVK injection from ``01_parameter_estimation``.

Same data and the same non-lensed parameter priors as tutorial 01
(chirp mass, luminosity distance → D1, coalescence time, phase). The only
addition is the two-image millilensing parameters (D2, t2, n1, n2).

An unlensed signal corresponds to a loud first image (D1 ≈ d_L) and a
negligible second image (large D2). With free phase, Type I and Type III
Morse factors (n1 = 0 and 1) are degenerate up to φ → φ + π.

Requires the 01 injection cache:

  output/01_parameter_estimation/bilby_run/injection_ifos.npz

Build that first with ``make bilby`` if it is missing.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import bilby
import corner
import matplotlib.pyplot as plt
import numpy as np
from bilby.core.prior import Uniform
from bilby.gw.conversion import convert_to_lal_binary_black_hole_parameters

from millilensing_two_image import (
    DiscreteUniformMorse,
    binary_black_hole_two_image_millilensing,
)
from plot_style import CORNER_KWARGS, apply_corner_style

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output" / "02_parameter_estimation_millisecondlens_on_unlensed"
RUN_DIR = OUTPUT_DIR / "bilby_run"
LABEL = "millilens_on_unlensed"

WAVEFORMS_PATH = OUTPUT_DIR / "lhvk_waveforms.png"
CORNER_USUAL_PATH = OUTPUT_DIR / "posterior_corner.png"
CORNER_LENS_PATH = OUTPUT_DIR / "posterior_corner_lens.png"
N1_PHASE_PATH = OUTPUT_DIR / "n1_vs_phase.png"
RESULT_PATH = RUN_DIR / f"{LABEL}_result.json"

NLIVE = 300
DLOGZ = 0.5


def _load_pe01():
    """Import 01_parameter_estimation.py (leading digit → load by path)."""
    path = ROOT / "01_parameter_estimation.py"
    spec = importlib.util.spec_from_file_location("pe01_parameter_estimation", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pe01 = _load_pe01()
IFO_CACHE_PATH = pe01.IFO_CACHE_PATH
INJECTION = pe01.INJECTION
TRIGGER_GPS = pe01.TRIGGER_GPS
DETECTORS = pe01.DETECTORS
DURATION = pe01.DURATION
SAMPLING_FREQUENCY = pe01.SAMPLING_FREQUENCY
START_FREQUENCY = pe01.START_FREQUENCY
REFERENCE_FREQUENCY = pe01.REFERENCE_FREQUENCY
WAVEFORM_APPROXIMANT = pe01.WAVEFORM_APPROXIMANT

# Same free CBC set as 01; luminosity_distance is represented by D1.
USUAL_PARAMETERS = ("chirp_mass", "D1", "geocent_time", "phase")
LENS_EXTRA_PARAMETERS = ("D2", "t2", "n1", "n2")
SAMPLED_PARAMETERS = USUAL_PARAMETERS + LENS_EXTRA_PARAMETERS

UNLENSED_TRUTH = dict(
    chirp_mass=INJECTION["chirp_mass"],
    D1=INJECTION["luminosity_distance"],
    geocent_time=INJECTION["geocent_time"],
    phase=INJECTION["phase"],
    n1=0.0,
)


def load_unlensed_injection() -> bilby.gw.detector.InterferometerList:
    """Reuse the exact LHVK strain cached by tutorial 01."""
    if not IFO_CACHE_PATH.exists():
        raise FileNotFoundError(
            f"Missing unlensed injection cache:\n  {IFO_CACHE_PATH}\n"
            "Run `make bilby` (or `uv run python 01_parameter_estimation.py`) first."
        )
    ifos = pe01.load_injection_cache()
    print(f"Loaded unlensed injection from {IFO_CACHE_PATH}")
    return ifos


def build_priors() -> bilby.core.prior.PriorDict:
    """Tutorial-01 CBC priors, plus millilensing extras (D2, t2, n1, n2)."""
    priors = pe01.build_priors()

    # Map 01's luminosity_distance prior onto D1 for the millilensing model.
    dL = priors["luminosity_distance"]
    del priors["luminosity_distance"]
    priors["D1"] = Uniform(
        dL.minimum,
        dL.maximum,
        name="D1",
        latex_label=r"$D_1$",
        unit="Mpc",
    )

    # Same D2 prior as tutorial 03 (unlensed data still prefers large D2).
    priors["D2"] = Uniform(
        200.0,
        2.0e3,
        name="D2",
        latex_label=r"$D_2$",
        unit="Mpc",
    )
    priors["t2"] = Uniform(
        1e-3,
        1e-1,
        name="t2",
        latex_label=r"$t_2$",
        unit="s",
    )
    priors["n1"] = DiscreteUniformMorse(name="n1", latex_label=r"$n_1$")
    priors["n2"] = DiscreteUniformMorse(name="n2", latex_label=r"$n_2$")
    return priors


def make_millilensing_waveform_generator() -> bilby.gw.waveform_generator.WaveformGenerator:
    return bilby.gw.waveform_generator.WaveformGenerator(
        duration=DURATION,
        sampling_frequency=SAMPLING_FREQUENCY,
        frequency_domain_source_model=binary_black_hole_two_image_millilensing,
        parameter_conversion=convert_to_lal_binary_black_hole_parameters,
        waveform_arguments=dict(
            waveform_approximant=WAVEFORM_APPROXIMANT,
            reference_frequency=REFERENCE_FREQUENCY,
            minimum_frequency=START_FREQUENCY,
        ),
    )


def plot_lhvk_waveforms(
    ifos: bilby.gw.detector.InterferometerList,
    outpath: Path,
) -> None:
    """Data from 01 plus the unlensed injected template (same as tutorial 01)."""
    unlensed_wfg = pe01.make_waveform_generator()
    clean_ifos = bilby.gw.detector.InterferometerList(DETECTORS)
    clean_ifos.set_strain_data_from_zero_noise(
        sampling_frequency=SAMPLING_FREQUENCY,
        duration=DURATION,
        start_time=INJECTION["geocent_time"] - DURATION + 2.0,
    )
    clean_ifos.inject_signal(
        waveform_generator=unlensed_wfg,
        parameters=INJECTION,
    )

    fig, axes = plt.subplots(
        len(ifos),
        1,
        figsize=(10, 2.4 * len(ifos)),
        sharex=True,
        constrained_layout=True,
    )
    if len(ifos) == 1:
        axes = [axes]

    time_relative = ifos[0].strain_data.time_array - INJECTION["geocent_time"]
    zoom = (time_relative > -0.3) & (time_relative < 0.15)

    for axis, ifo, clean_ifo in zip(axes, ifos, clean_ifos, strict=True):
        axis.plot(
            time_relative[zoom],
            ifo.strain_data.time_domain_strain[zoom],
            lw=0.7,
            color="0.75",
            label="data (01 unlensed inj.)",
        )
        axis.plot(
            time_relative[zoom],
            clean_ifo.strain_data.time_domain_strain[zoom],
            lw=1.2,
            color="C0",
            label="unlensed template",
        )
        axis.set_ylabel(f"{ifo.name}\nstrain")
        axis.grid(True, alpha=0.35)

    axes[0].legend(loc="upper left", fontsize=8)
    axes[0].set_title("Unlensed LHVK injection (shared with tutorial 01)")
    axes[-1].set_xlabel(r"Time relative to $t_c$ [s]")
    fig.savefig(outpath, dpi=150)
    plt.close(fig)


def _corner_ranges(columns, truths, pad_frac: float = 0.05):
    ranges = []
    for col, truth in zip(columns, truths, strict=True):
        arr = np.asarray(col, dtype=float)
        vals = [np.min(arr), np.max(arr)]
        if truth is not None and np.isfinite(truth):
            vals.extend([truth])
        lo, hi = float(min(vals)), float(max(vals))
        pad = pad_frac * (hi - lo) if hi > lo else 0.01
        ranges.append((lo - pad, hi + pad))
    return ranges


def plot_usual_posteriors(
    result: bilby.core.result.Result,
    outpath: Path,
) -> None:
    """Corner of the tutorial-01 CBC parameters (D1 stands in for d_L)."""
    labels = {
        "chirp_mass": r"$\mathcal{M}$",
        "D1": r"$D_1$ / $d_L$ (Mpc)",
        "geocent_time": r"$\Delta t_c$ (s)",
        "phase": r"$\phi$",
    }
    samples = result.posterior[list(USUAL_PARAMETERS)].copy()
    samples["geocent_time"] -= TRIGGER_GPS
    samples["phase"] = np.mod(samples["phase"], np.pi)

    truths = {
        "chirp_mass": UNLENSED_TRUTH["chirp_mass"],
        "D1": UNLENSED_TRUTH["D1"],
        "geocent_time": 0.0,
        "phase": float(np.mod(UNLENSED_TRUTH["phase"], np.pi)),
    }
    truth_list = [truths[name] for name in USUAL_PARAMETERS]
    ranges = _corner_ranges(
        [samples[name].to_numpy() for name in USUAL_PARAMETERS],
        truth_list,
    )
    apply_corner_style()
    fig = corner.corner(
        samples.values,
        labels=[labels[name] for name in USUAL_PARAMETERS],
        truths=truth_list,
        range=ranges,
        **CORNER_KWARGS,
    )
    fig.savefig(outpath, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_lens_posteriors(
    result: bilby.core.result.Result,
    outpath: Path,
) -> None:
    """Corner of image parameters (D1, D2, t1, t2, n1, n2)."""
    corner_names = ("D1", "D2", "t1", "t2", "n1", "n2")
    gps_epoch = int(np.floor(INJECTION["geocent_time"]))
    labels = {
        "D1": r"$D_1$ (Mpc)",
        "D2": r"$D_2$ (Mpc)",
        "t1": rf"$t_1$ (GPS $-$ {gps_epoch})",
        "t2": rf"$t_2$ (GPS $-$ {gps_epoch})",
        "n1": r"$n_1$",
        "n2": r"$n_2$",
    }
    t1_gps = result.posterior["geocent_time"].to_numpy()
    delay = result.posterior["t2"].to_numpy()
    samples = {
        "D1": result.posterior["D1"].to_numpy(),
        "D2": result.posterior["D2"].to_numpy(),
        "t1": t1_gps - gps_epoch,
        "t2": t1_gps + delay - gps_epoch,
        "n1": result.posterior["n1"].to_numpy(),
        "n2": result.posterior["n2"].to_numpy(),
    }
    truths = {
        "D1": UNLENSED_TRUTH["D1"],
        "D2": np.nan,
        "t1": INJECTION["geocent_time"] - gps_epoch,
        "t2": np.nan,
        "n1": UNLENSED_TRUTH["n1"],
        "n2": np.nan,
    }
    plot_ranges = []
    for name in corner_names:
        col = np.asarray(samples[name], dtype=float)
        if name in ("n1", "n2"):
            plot_ranges.append((-0.1, 1.1))
        elif np.ptp(col) == 0.0:
            center = float(col[0])
            pad = 0.05 if name in ("t1", "t2") else max(0.05 * abs(center), 1.0)
            plot_ranges.append((center - pad, center + pad))
        else:
            truth = truths[name]
            vals = [np.min(col), np.max(col)]
            if np.isfinite(truth):
                vals.append(float(truth))
            lo, hi = float(min(vals)), float(max(vals))
            pad = 0.05 * (hi - lo) if hi > lo else 0.01
            plot_ranges.append((lo - pad, hi + pad))
    apply_corner_style()
    fig = corner.corner(
        np.column_stack([samples[name] for name in corner_names]),
        labels=[labels[name] for name in corner_names],
        truths=[truths[name] for name in corner_names],
        range=plot_ranges,
        **CORNER_KWARGS,
    )
    fig.savefig(outpath, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_n1_vs_phase(
    result: bilby.core.result.Result,
    outpath: Path,
) -> None:
    """Diagnostic: Type I/III Morse factor vs coalescence phase."""
    n1 = result.posterior["n1"].to_numpy()
    phase = np.mod(result.posterior["phase"].to_numpy(), np.pi)
    apply_corner_style()
    fig, ax = plt.subplots(figsize=(5.5, 4.2))
    rng = np.random.default_rng(0)
    ax.scatter(
        phase,
        n1 + rng.normal(0.0, 0.015, size=n1.size),
        s=8,
        alpha=0.35,
        c="C0",
        edgecolors="none",
        label="posterior samples",
    )
    ax.axhline(0.0, color="0.5", lw=0.8, ls="--")
    ax.axhline(1.0, color="0.5", lw=0.8, ls="--")
    ax.axvline(
        np.mod(INJECTION["phase"], np.pi),
        color="C3",
        lw=1.0,
        label=r"injection $\phi$",
    )
    ax.axvline(
        np.mod(INJECTION["phase"] + np.pi, np.pi),
        color="C3",
        lw=1.0,
        ls=":",
        label=r"injection $\phi+\pi$ (mod $\pi$)",
    )
    ax.set_xlabel(r"coalescence phase $\phi$")
    ax.set_ylabel(r"$n_1$")
    ax.set_yticks([0.0, 0.5, 1.0])
    ax.set_ylim(-0.15, 1.15)
    ax.set_xlim(0.0, np.pi)
    ax.set_title(r"$n_1$–$\phi$ (Type I $\leftrightarrow$ Type III degeneracy)")
    ax.legend(loc="best", frameon=True, fontsize=9)
    fig.tight_layout()
    fig.savefig(outpath, dpi=150, bbox_inches="tight")
    plt.close(fig)


def print_recovery_summary(result: bilby.core.result.Result) -> None:
    print("\nUsual CBC recovery (same priors as tutorial 01; D1 ≡ d_L):")
    for name in USUAL_PARAMETERS:
        series = result.posterior[name]
        injected = UNLENSED_TRUTH[name]
        if name == "geocent_time":
            series = series - TRIGGER_GPS
            injected = 0.0
        if name == "phase":
            series = np.mod(series, np.pi)
            injected = float(np.mod(injected, np.pi))
        median = float(series.median())
        low, high = np.quantile(series, [0.16, 0.84])
        print(
            f"  {name:14s} truth={injected:12.4g}  "
            f"median={median:12.4g}  68%=[{low:.4g}, {high:.4g}]"
        )

    print(
        "\nLens extras (unlensed expectation: large D2; "
        "n1 ∈ {0,1} degenerate with φ → φ+π):"
    )
    for name in LENS_EXTRA_PARAMETERS:
        series = result.posterior[name]
        median = float(series.median())
        low, high = np.quantile(series, [0.16, 0.84])
        truth = UNLENSED_TRUTH.get(name)
        truth_str = f"{truth:12.4g}" if truth is not None else f"{'—':>12s}"
        print(
            f"  {name:14s} truth≈{truth_str}  "
            f"median={median:12.4g}  68%=[{low:.4g}, {high:.4g}]"
        )
    print(
        f"\n  lnZ = {result.log_evidence:.3f} ± {result.log_evidence_err:.3f}  "
        f"(ln B_{{signal/noise}} = {result.log_bayes_factor:.3f})"
    )


def products_complete() -> bool:
    return (
        WAVEFORMS_PATH.exists()
        and CORNER_USUAL_PATH.exists()
        and CORNER_LENS_PATH.exists()
        and N1_PHASE_PATH.exists()
        and RESULT_PATH.exists()
    )


def run_or_resume_sampler(
    ifos: bilby.gw.detector.InterferometerList,
    waveform_generator: bilby.gw.waveform_generator.WaveformGenerator,
    priors: bilby.core.prior.PriorDict,
) -> bilby.core.result.Result:
    if RESULT_PATH.exists():
        print(f"Loading existing bilby result from {RESULT_PATH}")
        return bilby.core.result.read_in_result(filename=str(RESULT_PATH))

    likelihood = bilby.gw.likelihood.GravitationalWaveTransient(
        interferometers=ifos,
        waveform_generator=waveform_generator,
        priors=priors,
    )

    resume_path = RUN_DIR / f"{LABEL}_resume.pickle"
    if resume_path.exists():
        print(f"Resuming dynesty from checkpoint {resume_path}")
    else:
        print(
            f"Running dynesty on {len(SAMPLED_PARAMETERS)} parameters "
            f"({', '.join(SAMPLED_PARAMETERS)}) with "
            f"{len(DETECTORS)} detectors, nlive={NLIVE} …"
        )

    return bilby.run_sampler(
        likelihood=likelihood,
        priors=priors,
        sampler="dynesty",
        nlive=NLIVE,
        dlogz=DLOGZ,
        npool=1,
        outdir=str(RUN_DIR),
        label=LABEL,
        resume=True,
        check_point_plot=False,
        plot=False,
    )


def main() -> None:
    bilby.core.utils.setup_logger(log_level="INFO")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    if products_complete():
        print(
            "Products already present; nothing to do.\n"
            f"  {WAVEFORMS_PATH}\n"
            f"  {CORNER_USUAL_PATH}\n"
            f"  {CORNER_LENS_PATH}\n"
            f"  {N1_PHASE_PATH}\n"
            f"  {RESULT_PATH}"
        )
        return

    priors = build_priors()
    waveform_generator = make_millilensing_waveform_generator()
    ifos = load_unlensed_injection()

    if not WAVEFORMS_PATH.exists():
        plot_lhvk_waveforms(ifos, WAVEFORMS_PATH)
        print(f"Wrote {WAVEFORMS_PATH}")
    else:
        print(f"Keeping existing {WAVEFORMS_PATH}")

    result = run_or_resume_sampler(ifos, waveform_generator, priors)

    if not CORNER_USUAL_PATH.exists():
        plot_usual_posteriors(result, CORNER_USUAL_PATH)
        print(f"Wrote {CORNER_USUAL_PATH}")
    else:
        print(f"Keeping existing {CORNER_USUAL_PATH}")

    if not CORNER_LENS_PATH.exists():
        plot_lens_posteriors(result, CORNER_LENS_PATH)
        print(f"Wrote {CORNER_LENS_PATH}")
    else:
        print(f"Keeping existing {CORNER_LENS_PATH}")

    if not N1_PHASE_PATH.exists():
        plot_n1_vs_phase(result, N1_PHASE_PATH)
        print(f"Wrote {N1_PHASE_PATH}")
    else:
        print(f"Keeping existing {N1_PHASE_PATH}")

    print_recovery_summary(result)
    print(f"\nFigures and bilby output written under:\n  {OUTPUT_DIR}\n")


if __name__ == "__main__":
    main()
