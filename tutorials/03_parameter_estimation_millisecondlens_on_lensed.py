#!/usr/bin/env python3
"""
Millilensing PE on a *lensed* two-image LHVK injection.

CBC / sky setup matches tutorial 01 / 02; image 1 uses the same effective
distance as the unlensed ``d_L`` (D1 = 400 Mpc, n1 = 0). A second image is
injected at finite D2 with millisecond delay t2 and Morse factor n2 = 1/2.

Samples the usual CBC parameters (chirp mass, coalescence time, phase) plus
the two-image millilensing parameters (D1, D2, t2, n1, n2). Relative arrival
of image 1 is fixed at t1 ≡ 0; absolute timing is carried by geocent_time.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import bilby
import corner
import matplotlib.pyplot as plt
import numpy as np
from bilby.core.prior import DeltaFunction, Uniform
from bilby.gw.conversion import convert_to_lal_binary_black_hole_parameters

from millilensing_two_image import (
    DiscreteUniformMorse,
    binary_black_hole_two_image_millilensing,
)
from plot_style import CORNER_KWARGS, apply_corner_style

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output" / "03_parameter_estimation_millisecondlens_on_lensed"
RUN_DIR = OUTPUT_DIR / "bilby_run"
LABEL = "millilens_on_lensed"

WAVEFORMS_PATH = OUTPUT_DIR / "lhvk_waveforms.png"
CORNER_USUAL_PATH = OUTPUT_DIR / "posterior_corner.png"
CORNER_LENS_PATH = OUTPUT_DIR / "posterior_corner_lens.png"
RESULT_PATH = RUN_DIR / f"{LABEL}_result.json"
IFO_CACHE_PATH = RUN_DIR / "injection_ifos.npz"

# Nested sampling: 6 continuous + 2 discrete Morse factors.
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
TRIGGER_GPS = pe01.TRIGGER_GPS
DETECTORS = pe01.DETECTORS
DURATION = pe01.DURATION
SAMPLING_FREQUENCY = pe01.SAMPLING_FREQUENCY
START_FREQUENCY = pe01.START_FREQUENCY
REFERENCE_FREQUENCY = pe01.REFERENCE_FREQUENCY
WAVEFORM_APPROXIMANT = pe01.WAVEFORM_APPROXIMANT

# Image 1 matches the unlensed 01 / 02 loud-image scale; image 2 is detectable.
LENS_INJECTION = dict(
    D1=pe01.INJECTION["luminosity_distance"],  # 400 Mpc
    D2=600.0,
    t2=2.0e-2,
    n1=0.0,
    n2=0.5,
)

INJECTION = {
    key: value
    for key, value in pe01.INJECTION.items()
    if key != "luminosity_distance"
}
INJECTION.update(LENS_INJECTION)
# Bilby source-frame metadata; waveform amplitude still uses D1 (see millilensing model).
INJECTION["luminosity_distance"] = LENS_INJECTION["D1"]

USUAL_PARAMETERS = ("chirp_mass", "geocent_time", "phase")
# t1 ≡ 0 in the waveform model; absolute image-1 time is geocent_time.
LENS_PARAMETERS = ("D1", "D2", "t2", "n1", "n2")
SAMPLED_PARAMETERS = USUAL_PARAMETERS + LENS_PARAMETERS


def build_priors() -> bilby.core.prior.PriorDict:
    """Sample usual CBC + millilensing observables; freeze the rest at injection."""
    priors = bilby.core.prior.PriorDict()
    priors["chirp_mass"] = Uniform(
        INJECTION["chirp_mass"] - 6.0,
        INJECTION["chirp_mass"] + 6.0,
        name="chirp_mass",
        latex_label=r"$\mathcal{M}$",
    )
    priors["geocent_time"] = Uniform(
        INJECTION["geocent_time"] - 0.04,
        INJECTION["geocent_time"] + 0.04,
        name="geocent_time",
        latex_label=r"$t_1\,\mathrm{(GPS)}$",
    )
    priors["phase"] = Uniform(
        0.0,
        np.pi,
        name="phase",
        latex_label=r"$\phi$",
        boundary="periodic",
    )
    priors["D1"] = Uniform(
        150.0,
        800.0,
        name="D1",
        latex_label=r"$d_{L,1}$",
        unit="Mpc",
    )
    priors["D2"] = Uniform(
        200.0,
        2.0e3,
        name="D2",
        latex_label=r"$d_{L,2}$",
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

    for key, value in INJECTION.items():
        if key in SAMPLED_PARAMETERS or key == "luminosity_distance":
            continue  # luminosity_distance is metadata alias of D1
        priors[key] = DeltaFunction(value, name=key)
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


def create_injection(
    waveform_generator: bilby.gw.waveform_generator.WaveformGenerator,
) -> bilby.gw.detector.InterferometerList:
    ifos = bilby.gw.detector.InterferometerList(DETECTORS)
    ifos.set_strain_data_from_power_spectral_densities(
        sampling_frequency=SAMPLING_FREQUENCY,
        duration=DURATION,
        start_time=INJECTION["geocent_time"] - DURATION + 2.0,
    )
    ifos.inject_signal(
        waveform_generator=waveform_generator,
        parameters=INJECTION,
    )
    return ifos


def save_injection_cache(ifos: bilby.gw.detector.InterferometerList) -> None:
    payload = {
        "detectors": np.array([ifo.name for ifo in ifos]),
        "start_time": float(ifos[0].strain_data.start_time),
        "duration": float(DURATION),
        "sampling_frequency": float(SAMPLING_FREQUENCY),
    }
    for ifo in ifos:
        payload[f"{ifo.name}_frequency_domain_strain"] = np.asarray(
            ifo.strain_data.frequency_domain_strain
        )
    np.savez_compressed(IFO_CACHE_PATH, **payload)


def load_injection_cache() -> bilby.gw.detector.InterferometerList:
    with np.load(IFO_CACHE_PATH, allow_pickle=False) as cache:
        detectors = [str(name) for name in cache["detectors"]]
        start_time = float(cache["start_time"])
        duration = float(cache["duration"])
        sampling_frequency = float(cache["sampling_frequency"])
        strains = {
            name: np.array(cache[f"{name}_frequency_domain_strain"])
            for name in detectors
        }

    ifos = bilby.gw.detector.InterferometerList(detectors)
    for ifo in ifos:
        ifo.set_strain_data_from_frequency_domain_strain(
            frequency_domain_strain=strains[ifo.name],
            sampling_frequency=sampling_frequency,
            duration=duration,
            start_time=start_time,
        )
    return ifos


def load_or_create_injection(
    waveform_generator: bilby.gw.waveform_generator.WaveformGenerator,
) -> bilby.gw.detector.InterferometerList:
    """Reuse the same LHVK strain on resume so likelihood matches the checkpoint."""
    if IFO_CACHE_PATH.exists():
        ifos = load_injection_cache()
        print(f"Loaded cached lensed injection from {IFO_CACHE_PATH}")
        return ifos

    ifos = create_injection(waveform_generator)
    save_injection_cache(ifos)
    print(f"Cached lensed injection to {IFO_CACHE_PATH}")
    return ifos


def plot_lhvk_waveforms(
    ifos: bilby.gw.detector.InterferometerList,
    waveform_generator: bilby.gw.waveform_generator.WaveformGenerator,
    outpath: Path,
) -> None:
    clean_ifos = bilby.gw.detector.InterferometerList(DETECTORS)
    clean_ifos.set_strain_data_from_zero_noise(
        sampling_frequency=SAMPLING_FREQUENCY,
        duration=DURATION,
        start_time=INJECTION["geocent_time"] - DURATION + 2.0,
    )
    clean_ifos.inject_signal(
        waveform_generator=waveform_generator,
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
    # Wider than 01/02 so the delayed image at t2 is visible.
    zoom = (time_relative > -0.3) & (time_relative < 0.25)

    for axis, ifo, clean_ifo in zip(axes, ifos, clean_ifos, strict=True):
        axis.plot(
            time_relative[zoom],
            ifo.strain_data.time_domain_strain[zoom],
            lw=0.7,
            color="0.75",
            label="data (noise + lensed signal)",
        )
        axis.plot(
            time_relative[zoom],
            clean_ifo.strain_data.time_domain_strain[zoom],
            lw=1.2,
            color="C0",
            label="lensed template",
        )
        axis.axvline(
            INJECTION["t2"],
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
        rf"Two-image millilensed LHVK injection "
        rf"($d_{{L,1}}={INJECTION['D1']:.0f}\,\mathrm{{Mpc}}$, "
        rf"$d_{{L,2}}={INJECTION['D2']:.0f}\,\mathrm{{Mpc}}$, "
        rf"$t_2={INJECTION['t2'] * 1e3:.0f}\,\mathrm{{ms}}$)"
    )
    axes[-1].set_xlabel(r"Time relative to $t_1$ [s]")
    fig.savefig(outpath, dpi=150)
    plt.close(fig)


def _corner_ranges(columns, truths, pad_frac: float = 0.05):
    """Axis ranges that include both posterior samples and truth markers."""
    ranges = []
    for col, truth in zip(columns, truths, strict=True):
        arr = np.asarray(col, dtype=float)
        lo = float(min(np.min(arr), truth))
        hi = float(max(np.max(arr), truth))
        pad = pad_frac * (hi - lo) if hi > lo else 0.01
        ranges.append((lo - pad, hi + pad))
    return ranges


def _pull_str(median, injected, low, high) -> str:
    sigma = 0.5 * (high - low)
    if sigma <= 0:
        return ""
    pull = (median - injected) / sigma
    return f"  pull≈{pull:+.1f}σ"


def plot_usual_posteriors(
    result: bilby.core.result.Result,
    outpath: Path,
) -> None:
    labels = {
        "chirp_mass": r"$\mathcal{M}$",
        "geocent_time": r"$\Delta t_1$ (s)",
        "phase": r"$\phi$",
    }
    samples = result.posterior[list(USUAL_PARAMETERS)].copy()
    samples["geocent_time"] -= TRIGGER_GPS
    samples["phase"] = np.mod(samples["phase"], np.pi)

    truths = {
        name: INJECTION[name] - (TRIGGER_GPS if name == "geocent_time" else 0.0)
        for name in USUAL_PARAMETERS
    }
    truths["phase"] = np.mod(truths["phase"], np.pi)
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
    """Corner of image parameters (dL1, dL2, t1, t2, n1, n2)."""
    # t1 ≡ 0 relative to geocent_time; show absolute Δt1 from TRIGGER_GPS.
    labels = [
        r"$d_{L,1}$ (Mpc)",
        r"$d_{L,2}$ (Mpc)",
        r"$\Delta t_1$ (s)",
        r"$t_2$ (s)",
        r"$n_1$",
        r"$n_2$",
    ]
    columns = [
        result.posterior["D1"].to_numpy(),
        result.posterior["D2"].to_numpy(),
        result.posterior["geocent_time"].to_numpy() - TRIGGER_GPS,
        result.posterior["t2"].to_numpy(),
        result.posterior["n1"].to_numpy(),
        result.posterior["n2"].to_numpy(),
    ]
    samples = np.column_stack(columns)
    truths = [
        INJECTION["D1"],
        INJECTION["D2"],
        INJECTION["geocent_time"] - TRIGGER_GPS,
        INJECTION["t2"],
        INJECTION["n1"],
        INJECTION["n2"],
    ]
    apply_corner_style()
    fig = corner.corner(
        samples,
        labels=labels,
        truths=truths,
        range=_corner_ranges(columns, truths),
        **CORNER_KWARGS,
    )
    fig.savefig(outpath, dpi=150, bbox_inches="tight")
    plt.close(fig)


def print_recovery_summary(result: bilby.core.result.Result) -> None:
    print("\nUsual-parameter recovery (50% / 68% intervals):")
    for name in USUAL_PARAMETERS:
        injected = INJECTION[name]
        series = result.posterior[name]
        if name == "geocent_time":
            injected -= TRIGGER_GPS
            series = series - TRIGGER_GPS
        if name == "phase":
            series = np.mod(series, np.pi)
            injected = np.mod(injected, np.pi)
        median = float(series.median())
        low, high = np.quantile(series, [0.16, 0.84])
        label = name if name != "geocent_time" else "geocent_time (Δt1)"
        print(
            f"  {label:22s} injected={injected:12.4g}  "
            f"median={median:12.4g}  68%=[{low:.4g}, {high:.4g}]"
            f"{_pull_str(median, injected, low, high)}"
        )

    print("\nImage-parameter recovery (t1 ≡ 0 relative to geocent_time):")
    for name in LENS_PARAMETERS:
        injected = INJECTION[name]
        series = result.posterior[name]
        median = float(series.median())
        low, high = np.quantile(series, [0.16, 0.84])
        print(
            f"  {name:8s} injected={injected:12.4g}  "
            f"median={median:12.4g}  68%=[{low:.4g}, {high:.4g}]"
            f"{_pull_str(median, injected, low, high)}"
        )


def products_complete() -> bool:
    return (
        WAVEFORMS_PATH.exists()
        and CORNER_USUAL_PATH.exists()
        and CORNER_LENS_PATH.exists()
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
            f"  {RESULT_PATH}"
        )
        return

    priors = build_priors()
    waveform_generator = make_millilensing_waveform_generator()
    ifos = load_or_create_injection(waveform_generator)

    if not WAVEFORMS_PATH.exists():
        plot_lhvk_waveforms(ifos, waveform_generator, WAVEFORMS_PATH)
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

    print_recovery_summary(result)
    print(f"\nFigures and bilby output written under:\n  {OUTPUT_DIR}\n")


if __name__ == "__main__":
    main()
