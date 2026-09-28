#!/usr/bin/env python3
"""
Fisher-matrix parameter-estimation demo with gwfast: synthetic BBH in LHVK.

Builds the network Fisher information matrix for a GW150914-like injection,
fixes all but chirp mass, luminosity distance, coalescence time, and
coalescence phase (same free set as the bilby / cogwheel tutorials), inverts
to a covariance, and draws a Gaussian corner from that covariance.

Typical runtime on a laptop CPU: about one minute (no nested sampling).

Re-runs are safe: completed products are left alone.
"""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path

import numpy as np

# gwfast still imports scipy.integrate.cumtrapz (removed in SciPy ≥ 1.14).
import scipy.integrate

if not hasattr(scipy.integrate, "cumtrapz"):
    scipy.integrate.cumtrapz = scipy.integrate.cumulative_trapezoid  # type: ignore[attr-defined]

import corner
import matplotlib.pyplot as plt
import gwfast.gwfastGlobals as glob
from gwfast.fisherTools import CovMatr, check_covariance, fixParams
from gwfast.gwfastUtils import GPSt_to_LMST, th_phi_from_ra_dec
from gwfast.network import DetNet
from plot_style import CORNER_KWARGS, apply_corner_style
from gwfast.signal import GWSignal
from gwfast.waveforms import IMRPhenomD

OUTPUT_DIR = Path(__file__).resolve().parent / "output" / "01_parameter_estimation_gwfast"
RUN_DIR = OUTPUT_DIR / "gwfast_run"

WAVEFORMS_PATH = OUTPUT_DIR / "lhvk_waveforms.png"
CORNER_PATH = OUTPUT_DIR / "posterior_corner.png"
RESULT_PATH = RUN_DIR / "fisher_result.json"
COVARIANCE_PATH = RUN_DIR / "covariance.npy"
FISHER_PATH = RUN_DIR / "fisher.npy"

# --- Analysis band / waveform ---
FMIN = 25.0
WAVEFORM_APPROXIMANT = "IMRPhenomD"

# LIGO Hanford, LIGO Livingston, Virgo, KAGRA (O4-era ASDs shipped with gwfast)
DETECTOR_KEYS = ("H1", "L1", "Virgo", "KAGRA")
PSD_DIR = Path(glob.detPath) / "observing_scenarios_paper"
PSD_FILES = {
    "H1": "aligo_O4high.txt",
    "L1": "aligo_O4high.txt",
    "Virgo": "avirgo_O4high_NEW.txt",
    "KAGRA": "kagra_80Mpc.txt",
}

# --- Injection truth (same masses / sky / distance as the bilby tutorial) ---
TRIGGER_GPS = 1_384_782_888.634
CHIRP_MASS = 28.6
MASS_RATIO = 0.83  # q = m2 / m1
ETA = MASS_RATIO / (1.0 + MASS_RATIO) ** 2
LUMINOSITY_DISTANCE_MPC = 400.0
RA = 1.95
DEC = -1.27
IOTA = 0.9
PSI = 0.82
PHASE = 0.5 * np.pi
CHI1Z = 0.0
CHI2Z = 0.0

# Free parameters in the Fisher (others fixed at the injection).
SAMPLED_PARAMETERS = ("Mc", "dL", "tcoal", "Phicoal")

# Convert gwfast native units → bilby-like display units for the corner.
# dL: Gpc → Mpc. tcoal in the Fisher/covariance is already in seconds
# (gwfast rescales ∂/∂tcoal from days → seconds before building F).
DISPLAY_SCALE = {
    "Mc": 1.0,
    "dL": 1_000.0,
    "tcoal": 1.0,
    "Phicoal": 1.0,
}
DISPLAY_NAMES = {
    "Mc": "chirp_mass",
    "dL": "luminosity_distance",
    "tcoal": "geocent_time",
    "Phicoal": "phase",
}
CORNER_LABELS = {
    "Mc": r"$\mathcal{M}$",
    "dL": r"$d_L$ (Mpc)",
    "tcoal": r"$\Delta t_c$ (s)",
    "Phicoal": r"$\phi$",
}

N_CORNER_SAMPLES = 20_000
CORNER_SEED = 42


def _as1(value: float) -> np.ndarray:
    return np.asarray([value], dtype=float)


def build_event() -> dict[str, np.ndarray]:
    theta, phi = th_phi_from_ra_dec(RA, DEC)
    theta = float(np.atleast_1d(theta)[0])
    phi = float(np.atleast_1d(phi)[0])
    tcoal = GPSt_to_LMST(_as1(TRIGGER_GPS), lat=0.0, long=0.0)
    return {
        "Mc": _as1(CHIRP_MASS),
        "eta": _as1(ETA),
        "dL": _as1(LUMINOSITY_DISTANCE_MPC / 1_000.0),  # gwfast uses Gpc
        "theta": _as1(theta),
        "phi": _as1(phi),
        "iota": _as1(IOTA),
        "psi": _as1(PSI),
        "tcoal": np.asarray(tcoal, dtype=float),
        "Phicoal": _as1(PHASE),
        "chi1z": _as1(CHI1Z),
        "chi2z": _as1(CHI2Z),
    }


def build_network() -> DetNet:
    detectors = copy.deepcopy(glob.detectors)
    signals: dict[str, GWSignal] = {}
    waveform = IMRPhenomD()
    for key in DETECTOR_KEYS:
        cfg = detectors[key]
        psd_path = PSD_DIR / PSD_FILES[key]
        if not psd_path.is_file():
            raise FileNotFoundError(f"Missing PSD for {key}: {psd_path}")
        signals[key] = GWSignal(
            waveform,
            psd_path=str(psd_path),
            detector_shape=cfg["shape"],
            det_lat=cfg["lat"],
            det_long=cfg["long"],
            det_xax=cfg["xax"],
            verbose=False,
            useEarthMotion=False,
            fmin=FMIN,
            IntTablePath=None,
        )
    return DetNet(signals, verbose=False)


def compute_fisher(
    net: DetNet,
    event: dict[str, np.ndarray],
) -> tuple[np.ndarray, dict[str, int], np.ndarray, float, np.ndarray]:
    """Return (F4, par_nums4, cov4, snr, inversion_error)."""
    snr = float(np.asarray(net.SNR(event)).reshape(-1)[0])
    fisher_full = net.FisherMatr(event)
    par_nums = IMRPhenomD().ParNums
    fixed = [name for name in par_nums if name not in SAMPLED_PARAMETERS]
    fisher, par_nums4 = fixParams(fisher_full, par_nums, fixed)
    covariance, inversion_error = CovMatr(fisher)
    check_covariance(fisher, covariance)
    return fisher, par_nums4, covariance, snr, np.asarray(inversion_error)


def covariance_in_display_units(
    covariance: np.ndarray,
    par_nums: dict[str, int],
) -> np.ndarray:
    """Scale the 4×4 covariance to (Msun, Mpc, s, rad)."""
    order = list(SAMPLED_PARAMETERS)
    cov = np.asarray(covariance[:, :, 0], dtype=float)
    # Reorder defensively in case fixParams changes key order.
    idx = [par_nums[name] for name in order]
    cov = cov[np.ix_(idx, idx)]
    scale = np.array([DISPLAY_SCALE[name] for name in order], dtype=float)
    return cov * np.outer(scale, scale)


def plot_lhvk_spectra(
    net: DetNet,
    event: dict[str, np.ndarray],
    outpath: Path,
) -> None:
    """Frequency-domain signal amplitude and noise ASD per detector."""
    names = list(net.signals.keys())
    fig, axes = plt.subplots(
        len(names),
        1,
        figsize=(10, 2.4 * len(names)),
        sharex=True,
        constrained_layout=True,
    )
    if len(names) == 1:
        axes = [axes]

    chi_s = 0.5 * (event["chi1z"] + event["chi2z"])
    chi_a = 0.5 * (event["chi1z"] - event["chi2z"])
    zeros = np.zeros_like(event["Mc"])

    for axis, name in zip(axes, names, strict=True):
        signal = net.signals[name]
        freqs = np.asarray(signal.strainFreq, dtype=float)
        mask = freqs >= FMIN
        strain = np.asarray(
            signal.GWstrain(
                freqs,
                event["Mc"],
                event["eta"],
                event["dL"],
                event["theta"],
                event["phi"],
                event["iota"],
                event["psi"],
                event["tcoal"],
                event["Phicoal"],
                chi_s,
                chi_a,
                zeros,
                zeros,
                zeros,
                zeros,
                zeros,
                zeros,
                zeros,
            ),
            dtype=complex,
        )
        asd = np.sqrt(np.asarray(signal.noiseCurve, dtype=float))
        axis.loglog(
            freqs[mask],
            asd[mask],
            color="0.45",
            lw=1.0,
            label="noise ASD",
        )
        axis.loglog(
            freqs[mask],
            np.abs(strain[mask]),
            color="C0",
            lw=1.2,
            label=r"$|h(f)|$",
        )
        axis.set_ylabel(f"{name}\nstrain / √Hz")
        axis.grid(True, which="both", alpha=0.35)
        axis.set_xlim(FMIN, 1_024.0)

    axes[0].legend(loc="upper right", fontsize=8)
    axes[0].set_title(
        f"Fisher tutorial injection in LHVK ({WAVEFORM_APPROXIMANT}, O4 ASDs)"
    )
    axes[-1].set_xlabel("Frequency [Hz]")
    fig.savefig(outpath, dpi=150)
    plt.close(fig)


def plot_fisher_corner(
    covariance_display: np.ndarray,
    outpath: Path,
) -> None:
    mean = np.array(
        [
            CHIRP_MASS,
            LUMINOSITY_DISTANCE_MPC,
            0.0,  # Δt_c
            PHASE,
        ],
        dtype=float,
    )
    rng = np.random.default_rng(CORNER_SEED)
    samples = rng.multivariate_normal(mean, covariance_display, size=N_CORNER_SAMPLES)
    apply_corner_style()
    fig = corner.corner(
        samples,
        labels=[CORNER_LABELS[name] for name in SAMPLED_PARAMETERS],
        truths=mean,
        **CORNER_KWARGS,
    )
    fig.savefig(outpath, dpi=150, bbox_inches="tight")
    plt.close(fig)


def print_recovery_summary(
    snr: float,
    covariance_display: np.ndarray,
    inversion_error: np.ndarray,
) -> None:
    truths = {
        "Mc": CHIRP_MASS,
        "dL": LUMINOSITY_DISTANCE_MPC,
        "tcoal": 0.0,
        "Phicoal": PHASE,
    }
    print(f"\nNetwork SNR: {snr:.2f}")
    print(f"Covariance inversion error: {float(np.asarray(inversion_error).reshape(-1)[0]):.3e}")
    print("\nFisher 1σ uncertainties (other parameters fixed at injection):")
    for i, name in enumerate(SAMPLED_PARAMETERS):
        sigma = float(np.sqrt(covariance_display[i, i]))
        injected = truths[name]
        label = DISPLAY_NAMES[name]
        if name == "tcoal":
            label = "geocent_time (Δt_c)"
        print(
            f"  {label:22s} injected={injected:12.4g}  "
            f"sigma={sigma:12.4g}"
        )


def save_result(
    snr: float,
    fisher: np.ndarray,
    covariance: np.ndarray,
    covariance_display: np.ndarray,
    par_nums: dict[str, int],
    inversion_error: np.ndarray,
) -> None:
    np.save(FISHER_PATH, fisher)
    np.save(COVARIANCE_PATH, covariance)
    sigmas = {
        DISPLAY_NAMES[name]: float(np.sqrt(covariance_display[i, i]))
        for i, name in enumerate(SAMPLED_PARAMETERS)
    }
    payload = {
        "approximant": WAVEFORM_APPROXIMANT,
        "detectors": list(DETECTOR_KEYS),
        "psd_files": PSD_FILES,
        "fmin_Hz": FMIN,
        "snr": snr,
        "inversion_error": float(np.asarray(inversion_error).reshape(-1)[0]),
        "sampled_parameters": list(SAMPLED_PARAMETERS),
        "parameter_indices": {k: int(v) for k, v in par_nums.items()},
        "injection": {
            "chirp_mass": CHIRP_MASS,
            "mass_ratio": MASS_RATIO,
            "eta": ETA,
            "luminosity_distance_Mpc": LUMINOSITY_DISTANCE_MPC,
            "ra": RA,
            "dec": DEC,
            "iota": IOTA,
            "psi": PSI,
            "phase": PHASE,
            "geocent_time": TRIGGER_GPS,
            "chi1z": CHI1Z,
            "chi2z": CHI2Z,
        },
        "sigma_display_units": sigmas,
        "display_units": {
            "chirp_mass": "Msun",
            "luminosity_distance": "Mpc",
            "geocent_time": "s (Delta t_c)",
            "phase": "rad",
        },
        "products": {
            "fisher": str(FISHER_PATH),
            "covariance": str(COVARIANCE_PATH),
            "waveforms": str(WAVEFORMS_PATH),
            "corner": str(CORNER_PATH),
        },
    }
    RESULT_PATH.write_text(json.dumps(payload, indent=2) + "\n")


def products_complete() -> bool:
    return (
        WAVEFORMS_PATH.exists()
        and CORNER_PATH.exists()
        and RESULT_PATH.exists()
        and COVARIANCE_PATH.exists()
        and FISHER_PATH.exists()
    )


def load_covariance_display() -> tuple[float, np.ndarray]:
    payload = json.loads(RESULT_PATH.read_text())
    covariance = np.load(COVARIANCE_PATH)
    par_nums = {k: int(v) for k, v in payload["parameter_indices"].items()}
    return float(payload["snr"]), covariance_in_display_units(covariance, par_nums)


def main() -> None:
    # Quiet some JAX allocator chatter on small machines.
    os.environ.setdefault("XLA_PYTHON_CLIENT_PREALLOCATE", "false")

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

    event = build_event()
    net = build_network()

    if RESULT_PATH.exists() and COVARIANCE_PATH.exists() and FISHER_PATH.exists():
        print(f"Loading existing Fisher result from {RESULT_PATH}")
        snr, covariance_display = load_covariance_display()
        inversion_error = np.array([json.loads(RESULT_PATH.read_text())["inversion_error"]])
    else:
        print(
            f"Computing gwfast Fisher matrix on {len(SAMPLED_PARAMETERS)} parameters "
            f"with {len(DETECTOR_KEYS)} detectors ({', '.join(DETECTOR_KEYS)}) …"
        )
        fisher, par_nums, covariance, snr, inversion_error = compute_fisher(net, event)
        covariance_display = covariance_in_display_units(covariance, par_nums)
        save_result(snr, fisher, covariance, covariance_display, par_nums, inversion_error)
        print(f"Wrote {RESULT_PATH}")

    if not WAVEFORMS_PATH.exists():
        plot_lhvk_spectra(net, event, WAVEFORMS_PATH)
        print(f"Wrote {WAVEFORMS_PATH}")
    else:
        print(f"Keeping existing {WAVEFORMS_PATH}")

    if not CORNER_PATH.exists():
        plot_fisher_corner(covariance_display, CORNER_PATH)
        print(f"Wrote {CORNER_PATH}")
    else:
        print(f"Keeping existing {CORNER_PATH}")

    print_recovery_summary(snr, covariance_display, inversion_error)
    print(f"\nFigures and gwfast output written under:\n  {OUTPUT_DIR}\n")


if __name__ == "__main__":
    main()
