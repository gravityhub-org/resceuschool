#!/usr/bin/env python3
"""
Fast parameter-estimation demo: synthetic BBH injected into the LHVK network.

Estimates chirp mass, luminosity distance, coalescence time, and coalescence
phase with bilby (other parameters fixed at the injection). Typical runtime on
a laptop CPU: ~10–20 minutes with the default sampler settings below.

Re-runs are safe: completed products are left alone, and an interrupted
dynesty run resumes from bilby's checkpoint using the saved injection data.
"""

from __future__ import annotations

from pathlib import Path

import bilby
import corner
import matplotlib.pyplot as plt
import numpy as np
from bilby.core.prior import DeltaFunction
from bilby.gw.conversion import convert_to_lal_binary_black_hole_parameters

OUTPUT_DIR = Path(__file__).resolve().parent / "output" / "01_parameter_estimation"
RUN_DIR = OUTPUT_DIR / "bilby_run"
LABEL = "lhvk_distance_demo"

WAVEFORMS_PATH = OUTPUT_DIR / "lhvk_waveforms.png"
CORNER_PATH = OUTPUT_DIR / "posterior_corner.png"
RESULT_PATH = RUN_DIR / f"{LABEL}_result.json"
IFO_CACHE_PATH = RUN_DIR / "injection_ifos.npz"

# --- Data segment ---
DURATION = 8.0
SAMPLING_FREQUENCY = 2048.0
START_FREQUENCY = 25.0
REFERENCE_FREQUENCY = 50.0
WAVEFORM_APPROXIMANT = "IMRPhenomD"

# LIGO Hanford, LIGO Livingston, Virgo, KAGRA (design / O4-era sensitivities in bilby)
DETECTORS = ["H1", "L1", "V1", "K1"]

# --- Nested sampling (tuned for ~10–20 min, 4-D posterior, LHVK) ---
# Need enough live points for stable corner contours (≪100 → ragged / empty levels).
NLIVE = 300
DLOGZ = 0.5

# --- Injection truth (GW150914-like masses and sky; distance chosen for strong LHVK SNR) ---
TRIGGER_GPS = 1_384_782_888.634
INJECTION = dict(
    chirp_mass=28.6,
    mass_ratio=0.83,
    luminosity_distance=400.0,
    geocent_time=TRIGGER_GPS,
    # π/2 sits away from the 0 / 2π prior edges (avoids railing in the corner).
    phase=0.5 * np.pi,
    ra=1.95,
    dec=-1.27,
    psi=0.82,
    theta_jn=0.9,
    # IMRPhenomD is non-precessing; use aligned spins for a stable tutorial run.
    a_1=0.0,
    a_2=0.0,
    tilt_1=0.0,
    tilt_2=0.0,
    phi_12=0.0,
    phi_jl=0.0,
)

SAMPLED_PARAMETERS = (
    "chirp_mass",
    "luminosity_distance",
    "geocent_time",
    "phase",
)


def build_priors() -> bilby.core.prior.PriorDict:
    priors = bilby.core.prior.PriorDict()
    priors["chirp_mass"] = bilby.core.prior.Uniform(
        INJECTION["chirp_mass"] - 6.0,
        INJECTION["chirp_mass"] + 6.0,
        name="chirp_mass",
        latex_label=r"$\mathcal{M}$",
    )
    priors["luminosity_distance"] = bilby.core.prior.Uniform(
        150.0,
        800.0,
        name="luminosity_distance",
        latex_label=r"$d_L\,\mathrm{(Mpc)}$",
    )
    priors["geocent_time"] = bilby.core.prior.Uniform(
        INJECTION["geocent_time"] - 0.04,
        INJECTION["geocent_time"] + 0.04,
        name="geocent_time",
        latex_label=r"$\Delta t_c\,\mathrm{(s)}$",
    )
    priors["phase"] = bilby.core.prior.Uniform(
        0.0,
        np.pi,
        name="phase",
        latex_label=r"$\phi$",
        boundary="periodic",
    )
    for key, value in INJECTION.items():
        if key not in SAMPLED_PARAMETERS:
            priors[key] = DeltaFunction(value, name=key)
    return priors


def make_waveform_generator() -> bilby.gw.waveform_generator.WaveformGenerator:
    return bilby.gw.waveform_generator.WaveformGenerator(
        duration=DURATION,
        sampling_frequency=SAMPLING_FREQUENCY,
        frequency_domain_source_model=bilby.gw.source.lal_binary_black_hole,
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
        print(f"Loaded cached injection from {IFO_CACHE_PATH}")
        return ifos

    ifos = create_injection(waveform_generator)
    save_injection_cache(ifos)
    print(f"Cached injection to {IFO_CACHE_PATH}")
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
    zoom = (time_relative > -0.3) & (time_relative < 0.15)

    for axis, ifo, clean_ifo in zip(axes, ifos, clean_ifos, strict=True):
        noisy = ifo.strain_data.time_domain_strain
        template = clean_ifo.strain_data.time_domain_strain
        axis.plot(
            time_relative[zoom],
            noisy[zoom],
            lw=0.7,
            color="0.75",
            label="data (noise + signal)",
        )
        axis.plot(
            time_relative[zoom],
            template[zoom],
            lw=1.2,
            color="C0",
            label="injected template",
        )
        axis.set_ylabel(f"{ifo.name}\nstrain")
        axis.grid(True, alpha=0.35)

    axes[0].legend(loc="upper left", fontsize=8)
    axes[0].set_title("Synthetic BBH injection in the LHVK network")
    axes[-1].set_xlabel(r"Time relative to $t_c$ [s]")
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
    # Non-precessing waveforms are π-periodic in coalescence phase; fold to [0, π)
    # so the corner shows one mode centered on the π/2 injection.
    samples["phase"] = np.mod(samples["phase"], np.pi)

    truths = {
        name: INJECTION[name] - (TRIGGER_GPS if name == "geocent_time" else 0.0)
        for name in SAMPLED_PARAMETERS
    }
    truths["phase"] = np.mod(truths["phase"], np.pi)
    fig = corner.corner(
        samples.values,
        labels=[labels[name] for name in SAMPLED_PARAMETERS],
        truths=[truths[name] for name in SAMPLED_PARAMETERS],
        quantiles=[0.16, 0.5, 0.84],
        show_titles=True,
        title_fmt=".4g",
        title_kwargs={"fontsize": 10},
        bins=28,
        smooth=1.0,
        levels=(0.5, 0.9),
        plot_datapoints=False,
        fill_contours=True,
        max_n_ticks=4,
    )
    fig.savefig(outpath, dpi=150, bbox_inches="tight")
    plt.close(fig)


def print_recovery_summary(result: bilby.core.result.Result) -> None:
    print("\nInjection recovery (50% credible intervals):")
    for name in SAMPLED_PARAMETERS:
        injected = INJECTION[name]
        if name == "geocent_time":
            injected -= TRIGGER_GPS
        series = result.posterior[name]
        if name == "geocent_time":
            series = series - TRIGGER_GPS
        if name == "phase":
            series = np.mod(series, np.pi)
            injected = np.mod(injected, np.pi)
        median = series.median()
        low, high = np.quantile(series, [0.16, 0.84])
        label = name if name != "geocent_time" else "geocent_time (Δt_c)"
        print(
            f"  {label:22s} injected={injected:12.4g}  "
            f"median={median:12.4g}  68%=[{low:.4g}, {high:.4g}]"
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
            f"Running dynesty on {len(SAMPLED_PARAMETERS)} parameters with "
            f"{len(DETECTORS)} detectors ({', '.join(DETECTORS)}), nlive={NLIVE} …"
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
    waveform_generator = make_waveform_generator()
    ifos = load_or_create_injection(waveform_generator)

    if not WAVEFORMS_PATH.exists():
        plot_lhvk_waveforms(ifos, waveform_generator, WAVEFORMS_PATH)
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
