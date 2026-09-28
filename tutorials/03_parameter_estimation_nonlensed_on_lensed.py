#!/usr/bin/env python3
"""
Unlensed (tutorial 01) PE on the *lensed* two-image LHVK injection.

Loads the same cached interferometer strain as
``03_parameter_estimation_millisecondlens_on_lensed.py`` and recovers the usual
CBC parameters (chirp mass, luminosity distance, coalescence time, phase) with
an *unlensed* BBH waveform model. The misspecified model is intentional: the
corner shows how ignoring millilensing biases the usual parameters.

Shares the lensed strain cache with the millilensing-on-lensed tutorial:

  output/03_parameter_estimation_millisecondlens_on_lensed/bilby_run/injection_ifos.npz

Creates that cache on first run if it is missing (same injection as millilens-lensed).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import bilby
import corner
import matplotlib.pyplot as plt
import numpy as np

from plot_style import CORNER_KWARGS, apply_corner_style

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output" / "03_parameter_estimation_nonlensed_on_lensed"
RUN_DIR = OUTPUT_DIR / "bilby_run"
LABEL = "nonlensed_on_lensed"

WAVEFORMS_PATH = OUTPUT_DIR / "lhvk_waveforms.png"
CORNER_PATH = OUTPUT_DIR / "posterior_corner.png"
RESULT_PATH = RUN_DIR / f"{LABEL}_result.json"

NLIVE = 300
DLOGZ = 0.5


def _load_module(filename: str, module_name: str):
    path = ROOT / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pe01 = _load_module("01_parameter_estimation.py", "pe01_parameter_estimation")
pe03 = _load_module(
    "03_parameter_estimation_millisecondlens_on_lensed.py",
    "pe03_millilens_on_lensed",
)

IFO_CACHE_PATH = pe03.IFO_CACHE_PATH
TRIGGER_GPS = pe01.TRIGGER_GPS
DETECTORS = pe01.DETECTORS
DURATION = pe01.DURATION
SAMPLING_FREQUENCY = pe01.SAMPLING_FREQUENCY

# Unlensed-model PE uses luminosity_distance; mark image-1 D1 as the naive truth.
INJECTION_UNLENSED = dict(pe01.INJECTION)
INJECTION_UNLENSED["luminosity_distance"] = pe03.LENS_INJECTION["D1"]

SAMPLED_PARAMETERS = pe01.SAMPLED_PARAMETERS


def load_or_create_lensed_injection() -> bilby.gw.detector.InterferometerList:
    """Share the millilens-on-lensed strain cache (create it if missing)."""
    IFO_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if IFO_CACHE_PATH.exists():
        ifos = pe03.load_injection_cache()
        print(f"Loaded lensed injection from {IFO_CACHE_PATH}")
        return ifos

    lensed_wfg = pe03.make_millilensing_waveform_generator()
    ifos = pe03.create_injection(lensed_wfg)
    pe03.save_injection_cache(ifos)
    print(f"Cached shared lensed injection to {IFO_CACHE_PATH}")
    return ifos

def build_priors() -> bilby.core.prior.PriorDict:
    """Same 4-D priors as tutorial 01 (unlensed BBH model)."""
    return pe01.build_priors()


def make_unlensed_waveform_generator() -> bilby.gw.waveform_generator.WaveformGenerator:
    return pe01.make_waveform_generator()


def plot_lhvk_waveforms(
    ifos: bilby.gw.detector.InterferometerList,
    outpath: Path,
) -> None:
    """Lensed data plus the naive unlensed template at image-1 distance D1."""
    unlensed_wfg = make_unlensed_waveform_generator()
    clean_ifos = bilby.gw.detector.InterferometerList(DETECTORS)
    clean_ifos.set_strain_data_from_zero_noise(
        sampling_frequency=SAMPLING_FREQUENCY,
        duration=DURATION,
        start_time=INJECTION_UNLENSED["geocent_time"] - DURATION + 2.0,
    )
    clean_ifos.inject_signal(
        waveform_generator=unlensed_wfg,
        parameters=INJECTION_UNLENSED,
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

    time_relative = ifos[0].strain_data.time_array - INJECTION_UNLENSED["geocent_time"]
    zoom = (time_relative > -0.3) & (time_relative < 0.25)

    for axis, ifo, clean_ifo in zip(axes, ifos, clean_ifos, strict=True):
        axis.plot(
            time_relative[zoom],
            ifo.strain_data.time_domain_strain[zoom],
            lw=0.7,
            color="0.75",
            label="data (lensed inj.)",
        )
        axis.plot(
            time_relative[zoom],
            clean_ifo.strain_data.time_domain_strain[zoom],
            lw=1.2,
            color="C0",
            label=rf"unlensed template ($d_L=D_1={INJECTION_UNLENSED['luminosity_distance']:.0f}$ Mpc)",
        )
        axis.axvline(
            pe03.LENS_INJECTION["t2"],
            color="C1",
            ls="--",
            lw=0.9,
            alpha=0.8,
            label=r"$t_2$" if axis is axes[0] else None,
        )
        axis.set_ylabel(f"{ifo.name}\nstrain")
        axis.grid(True, alpha=0.35)

    axes[0].legend(loc="upper left", fontsize=8)
    axes[0].set_title(
        "Lensed LHVK injection analysed with an unlensed BBH model (tutorial 01 setup)"
    )
    axes[-1].set_xlabel(r"Time relative to $t_1$ [s]")
    fig.savefig(outpath, dpi=150)
    plt.close(fig)


def plot_parameter_posteriors(
    result: bilby.core.result.Result,
    outpath: Path,
) -> None:
    labels = {
        "chirp_mass": r"$\mathcal{M}$",
        "luminosity_distance": r"$d_L$ (Mpc)",
        "geocent_time": r"$\Delta t_c$ (s)",
        "phase": r"$\phi$",
    }
    samples = result.posterior[list(SAMPLED_PARAMETERS)].copy()
    samples["geocent_time"] -= TRIGGER_GPS
    samples["phase"] = np.mod(samples["phase"], np.pi)

    truths = {
        name: INJECTION_UNLENSED[name]
        - (TRIGGER_GPS if name == "geocent_time" else 0.0)
        for name in SAMPLED_PARAMETERS
    }
    truths["phase"] = np.mod(truths["phase"], np.pi)

    # Expand axes so naive truths remain visible when the misspecified-model
    # posterior is strongly biased away from the injection.
    ranges = []
    for name in SAMPLED_PARAMETERS:
        col = samples[name].to_numpy()
        truth = truths[name]
        lo = float(min(np.min(col), truth))
        hi = float(max(np.max(col), truth))
        pad = 0.05 * (hi - lo) if hi > lo else 0.01
        ranges.append((lo - pad, hi + pad))

    apply_corner_style()
    fig = corner.corner(
        samples.values,
        labels=[labels[name] for name in SAMPLED_PARAMETERS],
        truths=[truths[name] for name in SAMPLED_PARAMETERS],
        range=ranges,
        **CORNER_KWARGS,
    )
    fig.savefig(outpath, dpi=150, bbox_inches="tight")
    plt.close(fig)


def print_recovery_summary(result: bilby.core.result.Result) -> None:
    print(
        "\nUnlensed-model recovery on lensed data (50% / 68% intervals):\n"
        f"  (naive truth markers use image-1 D1 = "
        f"{INJECTION_UNLENSED['luminosity_distance']:.4g} Mpc; "
        "the unlensed model is misspecified — biases are expected)"
    )
    for name in SAMPLED_PARAMETERS:
        injected = INJECTION_UNLENSED[name]
        series = result.posterior[name]
        if name == "geocent_time":
            injected -= TRIGGER_GPS
            series = series - TRIGGER_GPS
        if name == "phase":
            series = np.mod(series, np.pi)
            injected = np.mod(injected, np.pi)
        median = float(series.median())
        low, high = np.quantile(series, [0.16, 0.84])
        sigma = 0.5 * (high - low)
        pull = (median - injected) / sigma if sigma > 0 else float("nan")
        label = name if name != "geocent_time" else "geocent_time (Δt_c)"
        print(
            f"  {label:22s} naive={injected:12.4g}  "
            f"median={median:12.4g}  68%=[{low:.4g}, {high:.4g}]  "
            f"pull≈{pull:+.1f}σ"
        )


def products_complete() -> bool:
    return (
        WAVEFORMS_PATH.exists()
        and CORNER_PATH.exists()
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
            f"Running dynesty on {len(SAMPLED_PARAMETERS)} unlensed parameters "
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
            f"  {CORNER_PATH}\n"
            f"  {RESULT_PATH}"
        )
        return

    priors = build_priors()
    waveform_generator = make_unlensed_waveform_generator()
    ifos = load_or_create_lensed_injection()

    if not WAVEFORMS_PATH.exists():
        plot_lhvk_waveforms(ifos, WAVEFORMS_PATH)
        print(f"Wrote {WAVEFORMS_PATH}")
    else:
        print(f"Keeping existing {WAVEFORMS_PATH}")

    result = run_or_resume_sampler(ifos, waveform_generator, priors)

    if not CORNER_PATH.exists():
        plot_parameter_posteriors(result, CORNER_PATH)
        print(f"Wrote {CORNER_PATH}")
    else:
        print(f"Keeping existing {CORNER_PATH}")

    print_recovery_summary(result)
    print(f"\nFigures and bilby output written under:\n  {OUTPUT_DIR}\n")


if __name__ == "__main__":
    main()
