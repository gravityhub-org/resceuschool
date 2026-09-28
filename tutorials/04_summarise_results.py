from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
from typing import NamedTuple

import bilby
import corner
import matplotlib.pyplot as plt
import numpy as np
from bilby.core.result import Result

# Plot style/paths
from plot_style import CORNER_KWARGS, apply_corner_style
ROOT = Path(__file__).resolve().parent # Take absolute filepath
OUTPUT_DIR = ROOT / "output" / "04_summarise_results"
COMPARISON_UNLENSED_PATH = OUTPUT_DIR / "comparison_unlensed_injection.png"
COMPARISON_LENSED_PATH = OUTPUT_DIR / "comparison_lensed_injection.png"
LENS_RECOVERY_UNLENSED_PATH = OUTPUT_DIR / "lens_recovery_unlensed_injection.png"
LENS_RECOVERY_LENSED_PATH = OUTPUT_DIR / "lens_recovery_lensed_injection.png"

# Distance is the analogous free amplitude parameter across models.
DISTANCE_ALIAS = ("luminosity_distance", "D1")

# Image-parameter corner order (t1 ≡ geocent_time − TRIGGER_GPS; t2 = delay).
LENS_CORNER_KEYS = ("D1", "D2", "t1", "t2", "n1", "n2")

PARAM_LABELS = {
    "chirp_mass": r"$\mathcal{M}$",
    "luminosity_distance": r"$d_L$ (Mpc)",
    "geocent_time": r"$\Delta t_c$ (s)",
    "phase": r"$\phi$",
    "D1": r"$d_{L,1}$ (Mpc)",
    "D2": r"$d_{L,2}$ (Mpc)",
    "t1": r"$\Delta t_1$ (s)",
    "t2": r"$t_2$ (s)",
    "n1": r"$n_1$",
    "n2": r"$n_2$",
    "distance": r"$d_L$ / $d_{L,1}$ (Mpc)",
}


def _load_pe01():
    path = ROOT / "01_parameter_estimation.py"
    spec = importlib.util.spec_from_file_location("pe01_parameter_estimation", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pe01 = _load_pe01()
TRIGGER_GPS = pe01.TRIGGER_GPS

# Tutorial scripts whose build_priors() define the PE runs summarised here.
PRIOR_SCRIPT_SPECS = (
    ("01", "01_parameter_estimation.py", "non-lensed model / unlensed data"),
    ("02", "02_parameter_estimation_millisecondlens_on_unlensed.py", "millilens / unlensed data"),
    ("03n", "03_parameter_estimation_nonlensed_on_lensed.py", "non-lensed model / lensed data"),
    ("03m", "03_parameter_estimation_millisecondlens_on_lensed.py", "millilens / lensed data"),
)

# Canonical name for cross-run comparison (script key → concept).
PRIOR_CONCEPT = {
    "chirp_mass": "chirp_mass",
    "luminosity_distance": "d_L_or_D1",
    "D1": "d_L_or_D1",
    "geocent_time": "geocent_time",
    "phase": "phase",
    "D2": "D2",
    "t2": "t2",
    "n1": "n1",
    "n2": "n2",
}


class RunSpec(NamedTuple):
    key: str
    label: str
    path: Path
    injection: str  # "unlensed" | "lensed"
    model: str  # "nonlensed" | "lensed"


def default_run_specs(results_root: Path | None = None) -> dict[str, RunSpec]:
    """Map short keys → result JSON paths (override root for tests)."""
    root = results_root if results_root is not None else ROOT / "output"
    return {
        "01": RunSpec(
            key="01",
            label="non-lensed model on unlensed injection",
            path=root
            / "01_parameter_estimation"
            / "bilby_run"
            / "lhvk_distance_demo_result.json",
            injection="unlensed",
            model="nonlensed",
        ),
        "02": RunSpec(
            key="02",
            label="millilensed model on unlensed injection",
            path=root
            / "02_parameter_estimation_millisecondlens_on_unlensed"
            / "bilby_run"
            / "millilens_on_unlensed_result.json",
            injection="unlensed",
            model="lensed",
        ),
        "03m": RunSpec(
            key="03m",
            label="millilensed model on lensed injection",
            path=root
            / "03_parameter_estimation_millisecondlens_on_lensed"
            / "bilby_run"
            / "millilens_on_lensed_result.json",
            injection="lensed",
            model="lensed",
        ),
        "03n": RunSpec(
            key="03n",
            label="non-lensed model on lensed injection",
            path=root
            / "03_parameter_estimation_nonlensed_on_lensed"
            / "bilby_run"
            / "nonlensed_on_lensed_result.json",
            injection="lensed",
            model="nonlensed",
        ),
    }


def _load_tutorial_module(filename: str, module_name: str):
    path = ROOT / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def format_prior(prior) -> str:
    """Compact string for a bilby prior, pulled from the live prior object."""
    cls = type(prior).__name__
    if cls == "DeltaFunction":
        peak = getattr(prior, "peak", None)
        try:
            return f"Delta({float(peak):.6g})"
        except (TypeError, ValueError):
            return f"Delta({peak})"
    if cls == "DiscreteUniformMorse":
        return "DiscreteUniformMorse{0,0.5,1}"
    if hasattr(prior, "minimum") and hasattr(prior, "maximum"):
        lo, hi = float(prior.minimum), float(prior.maximum)
        # Compact GPS coalescence window as tc±δ.
        if abs(lo - TRIGGER_GPS) < 1.0 and abs(hi - TRIGGER_GPS) < 1.0:
            return f"Uniform[tc{lo - TRIGGER_GPS:+.4g}, tc{hi - TRIGGER_GPS:+.4g}]"
        text = f"Uniform[{lo:.6g}, {hi:.6g}]"
        boundary = getattr(prior, "boundary", None)
        if boundary:
            text += f" ({boundary})"
        return text
    return f"{cls}({prior})"


def load_run_priors() -> dict[str, dict]:
    """Import each PE script and return its free (non-Delta) priors."""
    out: dict[str, dict] = {}
    for key, filename, label in PRIOR_SCRIPT_SPECS:
        module = _load_tutorial_module(filename, f"prior_module_{key}")
        priors = module.build_priors()
        sampled = tuple(getattr(module, "SAMPLED_PARAMETERS", ()))
        free = {
            name: priors[name]
            for name in priors.keys()
            if type(priors[name]).__name__ != "DeltaFunction"
        }
        out[key] = {
            "label": label,
            "script": filename,
            "sampled": sampled,
            "free_priors": free,
            "ifo_cache": getattr(module, "IFO_CACHE_PATH", None),
        }
    return out


def print_prior_table(run_priors: dict[str, dict] | None = None) -> None:
    """Print free priors from each script and whether shared concepts match."""
    runs = run_priors if run_priors is not None else load_run_priors()
    keys = [k for k, _, _ in PRIOR_SCRIPT_SPECS]

    print("\n(priors) Free priors pulled from each tutorial script")
    print("-" * 72)
    for key in keys:
        info = runs[key]
        print(f"  [{key}] {info['label']}")
        print(f"       script: {info['script']}")
        print(f"       sampled: {', '.join(info['sampled'])}")
        if info["ifo_cache"] is not None:
            print(f"       data:    {info['ifo_cache']}")
        for name, prior in info["free_priors"].items():
            print(f"       {name:22s}  {format_prior(prior)}")

    # Concept → run → formatted prior string
    by_concept: dict[str, dict[str, str]] = {}
    for key in keys:
        for name, prior in runs[key]["free_priors"].items():
            concept = PRIOR_CONCEPT.get(name, name)
            by_concept.setdefault(concept, {})[key] = f"{name}: {format_prior(prior)}"

    concepts = [
        "chirp_mass",
        "d_L_or_D1",
        "geocent_time",
        "phase",
        "D2",
        "t2",
        "n1",
        "n2",
    ]
    print("\n(priors) Shared-parameter comparability")
    print("-" * 72)
    header = f"  {'concept':16s}" + "".join(f"  {k:22s}" for k in keys) + "  comparable?"
    print(header)
    for concept in concepts:
        if concept not in by_concept:
            continue
        cells = []
        present = []
        for key in keys:
            if key in by_concept[concept]:
                # Drop the "name: " prefix for the cell; keep format_prior only.
                cell = by_concept[concept][key].split(": ", 1)[1]
                cells.append(cell)
                present.append(cell)
            else:
                cells.append("—")
        comparable = "yes" if len(set(present)) == 1 else ("n/a" if len(present) < 2 else "NO")
        row = f"  {concept:16s}" + "".join(f"  {c:22s}" for c in cells) + f"  {comparable}"
        print(row)

    # Data sharing
    print("\n(priors) Strain caches")
    print("-" * 72)
    caches = {key: runs[key]["ifo_cache"] for key in keys}
    print(f"  01 and 02 share cache: {caches['01'] == caches['02']}")
    print(f"    → {caches['01']}")
    print(f"  03n and 03m share cache: {caches['03n'] == caches['03m']}")
    print(f"    → {caches['03n']}")
    print(f"  unlensed vs lensed caches differ: {caches['01'] != caches['03n']}")


def load_results(run_specs: dict[str, RunSpec]) -> dict[str, Result]:
    missing = [f"  {spec.key}: {spec.path}" for spec in run_specs.values() if not spec.path.exists()]
    if missing:
        raise FileNotFoundError(
            "Missing bilby result file(s):\n"
            + "\n".join(missing)
            + "\nBuild with make bilby / millilens / millilens-lensed / nonlensed-on-lensed."
        )
    results: dict[str, Result] = {}
    for key, spec in run_specs.items():
        #print(f"Loading {spec.key}: {spec.path}")
        results[key] = bilby.core.result.read_in_result(filename=str(spec.path))
    return results


def format_pm(median: float, sigma: float, precision: str = ".4g") -> str:
    return f"({median:{precision}}±{sigma:{precision}})"


def one_sigma_summary(samples: np.ndarray) -> tuple[float, float]:
    """Median and symmetric 1-σ half-width from the 16–84% quantiles."""
    low, median, high = np.quantile(samples, [0.16, 0.5, 0.84])
    return float(median), float(0.5 * (high - low))


def prepare_series(name: str, series) -> np.ndarray:
    values = np.asarray(series, dtype=float)
    if name == "geocent_time":
        values = values - TRIGGER_GPS
    elif name == "phase":
        values = np.mod(values, np.pi)
    return values


def print_evidences(run_specs: dict[str, RunSpec], results: dict[str, Result]) -> None:
    print("Evidences")
    for key, spec in run_specs.items():
        result = results[key]
        print(
                f"  [{key}] {spec.label}: ln F = {result.log_evidence:.4f} ± {result.log_evidence_err:.4f}"
        )


def bayes_factor(result_lensed: Result, result_nonlensed: Result) -> tuple[float, float]:
    """Return (ln B_{L/NL}, σ_lnB)."""
    ln_bf = float(result_lensed.log_evidence - result_nonlensed.log_evidence)
    sigma = float(
        np.hypot(result_lensed.log_evidence_err, result_nonlensed.log_evidence_err)
    )
    return ln_bf, sigma


def print_bayes_factors(run_specs: dict[str, RunSpec], results: dict[str, Result]) -> None:
    print("Bayes factors (lensed model / non-lensed model)")
    pairs = (
        ("unlensed injection", "02", "01"),
        ("lensed injection", "03m", "03n"),
    )
    for title, key_l, key_nl in pairs:
        ln_bf, sigma = bayes_factor(results[key_l], results[key_nl])
        print(f"  {title}: ln B_{{L/NL}} = {ln_bf:.4f} ± {sigma:.4f}")
        #if abs(ln_bf) < 700:
        #    print(f"    B_{{L/NL}}    = {np.exp(ln_bf):.4g}")
        #else:
        #    print(f"    B_{{L/NL}}    = exp({ln_bf:.4f})  (overflow in float)")
        #print(f"    runs: {run_specs[key_l].key} / {run_specs[key_nl].key}")


def print_parameter_summaries(
    run_specs: dict[str, RunSpec], results: dict[str, Result]
) -> None:
    print("\n(c) Search parameters (median ± 1σ from 16–84% quantiles)")
    print("-" * 72)
    for key, spec in run_specs.items():
        result = results[key]
        print(f"  [{key}] {spec.label}")
        for name in result.search_parameter_keys:
            values = prepare_series(name, result.posterior[name])
            median, sigma = one_sigma_summary(values)
            display = "geocent_time (Δt_c)" if name == "geocent_time" else name
            print(f"    {display:24s}  {format_pm(median, sigma)}")


def shared_parameter_pairs(
    result_nonlensed: Result, result_lensed: Result
) -> list[tuple[str, str, str]]:
    """
    Canonical label + column names present in both models.

    Direct name matches use the search-parameter intersection. Distance is
    matched via luminosity_distance (non-lensed) ↔ D1 (millilensed).
    """
    keys_nl = set(result_nonlensed.search_parameter_keys)
    keys_l = set(result_lensed.search_parameter_keys)
    pairs: list[tuple[str, str, str]] = []
    for name in sorted(keys_nl & keys_l):
        pairs.append((name, name, name))
    nl_dist, l_dist = DISTANCE_ALIAS
    if nl_dist in keys_nl and l_dist in keys_l:
        pairs.append(("distance", nl_dist, l_dist))
    return pairs


def _aligned_samples(
    result: Result, column: str, n_draw: int, rng: np.random.Generator
) -> np.ndarray:
    values = prepare_series(column, result.posterior[column])
    if len(values) == n_draw:
        return values
    idx = rng.choice(len(values), size=n_draw, replace=len(values) < n_draw)
    return values[idx]


def plot_model_comparison(
    result_nonlensed: Result,
    result_lensed: Result,
    outpath: Path,
    title: str,
    seed: int = 0,
) -> list[tuple[str, str, str]]:
    """Overlay corner of shared parameters; return the pairs that were plotted."""
    pairs = shared_parameter_pairs(result_nonlensed, result_lensed)
    if not pairs:
        #print(f"  No shared parameters for '{title}'; skipping plot.")
        return pairs

    n_draw = min(len(result_nonlensed.posterior), len(result_lensed.posterior), 5000)
    rng = np.random.default_rng(seed)
    samples_nl = np.column_stack(
        [_aligned_samples(result_nonlensed, col, n_draw, rng) for _, col, _ in pairs]
    )
    samples_l = np.column_stack(
        [_aligned_samples(result_lensed, col, n_draw, rng) for _, _, col in pairs]
    )
    labels = [PARAM_LABELS.get(canon, canon) for canon, _, _ in pairs]

    apply_corner_style()
    kwargs = {**CORNER_KWARGS, "show_titles": False}
    fig = corner.corner(
        samples_nl,
        labels=labels,
        color="C0",
        hist_kwargs={"density": True, "color": "C0"},
        **kwargs,
    )
    corner.corner(
        samples_l,
        fig=fig,
        labels=labels,
        color="C1",
        hist_kwargs={"density": True, "color": "C1"},
        **kwargs,
    )
    fig.suptitle(title, y=1.02)
    # Simple colour legend on the first diagonal axis.
    axes = np.atleast_1d(fig.axes)
    axes[0].plot([], [], color="C0", label="non-lensed model")
    axes[0].plot([], [], color="C1", label="lensed model")
    axes[0].legend(loc="upper right", fontsize=10, frameon=True)

    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outpath, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return pairs


def print_and_plot_comparisons(
    results: dict[str, Result],
    output_dir: Path,
) -> dict[str, list[tuple[str, str, str]]]:
    #print("\n(d) Shared-parameter posterior comparisons")
    #print("-" * 72)
    output_dir.mkdir(parents=True, exist_ok=True)
    plotted = {
        "unlensed": plot_model_comparison(
            results["01"],
            results["02"],
            output_dir / "comparison_unlensed_injection.png",
            title="Unlensed injection: non-lensed vs millilensed model",
            seed=1,
        ),
        "lensed": plot_model_comparison(
            results["03n"],
            results["03m"],
            output_dir / "comparison_lensed_injection.png",
            title="Lensed injection: non-lensed vs millilensed model",
            seed=2,
        ),
    }
    for injection, pairs in plotted.items():
        if pairs:
            names = ", ".join(canon for canon, _, _ in pairs)
            #print(f"  {injection} injection shared parameters: {names}")
    return plotted


def lens_recovery_columns(result: Result) -> dict[str, np.ndarray]:
    """
    Build (D1, D2, t1, t2, n1, n2) from a millilensed posterior.

    t1 is geocent_time − TRIGGER_GPS (image-1 absolute time relative to the
    trigger); t2 is the relative image-2 delay sampled by the PE.
    """
    required = ("D1", "D2", "geocent_time", "t2", "n1", "n2")
    missing = [name for name in required if name not in result.posterior]
    if missing:
        raise KeyError(
            "Millilensed result missing columns for lens recovery plot: "
            + ", ".join(missing)
        )
    return {
        "D1": np.asarray(result.posterior["D1"], dtype=float),
        "D2": np.asarray(result.posterior["D2"], dtype=float),
        "t1": np.asarray(result.posterior["geocent_time"], dtype=float) - TRIGGER_GPS,
        "t2": np.asarray(result.posterior["t2"], dtype=float),
        "n1": np.asarray(result.posterior["n1"], dtype=float),
        "n2": np.asarray(result.posterior["n2"], dtype=float),
    }


def lens_recovery_truths(injection: str) -> dict[str, float]:
    """Truth markers for lens corners; NaN omits the marker in corner."""
    t1_truth = float(pe01.INJECTION["geocent_time"] - TRIGGER_GPS)
    d1_truth = float(pe01.INJECTION["luminosity_distance"])
    if injection == "lensed":
        pe03 = _load_tutorial_module(
            "03_parameter_estimation_millisecondlens_on_lensed.py",
            "pe03_for_lens_truths",
        )
        inj = pe03.INJECTION
        return {
            "D1": float(inj["D1"]),
            "D2": float(inj["D2"]),
            "t1": float(inj["geocent_time"] - TRIGGER_GPS),
            "t2": float(inj["t2"]),
            "n1": float(inj["n1"]),
            "n2": float(inj["n2"]),
        }
    if injection == "unlensed":
        return {
            "D1": d1_truth,
            "D2": np.nan,  # second image absent / unconstrained
            "t1": t1_truth,
            "t2": np.nan,
            "n1": 0.0,
            "n2": np.nan,
        }
    raise ValueError(f"Unknown injection kind: {injection!r}")


def _lens_corner_ranges(
    columns: dict[str, np.ndarray],
    truths: dict[str, float],
    pad_frac: float = 0.05,
) -> list[tuple[float, float]]:
    ranges: list[tuple[float, float]] = []
    for key in LENS_CORNER_KEYS:
        if key in ("n1", "n2"):
            ranges.append((-0.1, 1.1))
            continue
        arr = columns[key]
        vals = [float(np.min(arr)), float(np.max(arr))]
        truth = truths[key]
        if np.isfinite(truth):
            vals.append(float(truth))
        lo, hi = min(vals), max(vals)
        pad = pad_frac * (hi - lo) if hi > lo else 0.01
        ranges.append((lo - pad, hi + pad))
    return ranges


def plot_lens_recovery(
    result: Result,
    outpath: Path,
    title: str,
    truths: dict[str, float],
) -> list[str]:
    """Corner of image parameters (dL1, dL2, t1, t2, n1, n2) for one millilensed run."""
    columns = lens_recovery_columns(result)
    samples = np.column_stack([columns[key] for key in LENS_CORNER_KEYS])
    labels = [PARAM_LABELS[key] for key in LENS_CORNER_KEYS]
    truth_list = [truths[key] for key in LENS_CORNER_KEYS]

    apply_corner_style()
    fig = corner.corner(
        samples,
        labels=labels,
        truths=truth_list,
        range=_lens_corner_ranges(columns, truths),
        **CORNER_KWARGS,
    )
    fig.suptitle(title, y=1.02)
    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outpath, dpi=150, bbox_inches="tight")
    plt.close(fig)
    #print(f"  Wrote {outpath}")
    return list(LENS_CORNER_KEYS)


def print_and_plot_lens_recoveries(
    results: dict[str, Result],
    output_dir: Path,
) -> dict[str, list[str]]:
    #print("\n(e) Millilensed image-parameter recovery (dL1, dL2, t1, t2, n1, n2)")
    #print("-" * 72)
    output_dir.mkdir(parents=True, exist_ok=True)
    plotted = {
        "unlensed": plot_lens_recovery(
            results["02"],
            output_dir / "lens_recovery_unlensed_injection.png",
            title="Unlensed injection: millilensed image-parameter recovery",
            truths=lens_recovery_truths("unlensed"),
        ),
        "lensed": plot_lens_recovery(
            results["03m"],
            output_dir / "lens_recovery_lensed_injection.png",
            title="Lensed injection: millilensed image-parameter recovery",
            truths=lens_recovery_truths("lensed"),
        ),
    }
    #for injection, keys in plotted.items():
    #    print(f"  {injection} injection lens parameters: {', '.join(keys)}")
    return plotted


def summarise(
    run_specs: dict[str, RunSpec] | None = None,
    output_dir: Path | None = None,
    priors_only: bool = False,
) -> dict[str, Result] | None:
    #print_prior_table()
    if priors_only:
        return None
    specs = run_specs if run_specs is not None else default_run_specs()
    out = output_dir if output_dir is not None else OUTPUT_DIR
    results = load_results(specs)
    print_evidences(specs, results)
    print_bayes_factors(specs, results)
    #print_parameter_summaries(specs, results)
    print_and_plot_comparisons(results, out)
    print_and_plot_lens_recoveries(results, out)
    print(f"\nSummary figures under:\n  {out}")
    return results


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--priors-only",
        action="store_true",
        help="Only print free priors loaded from each PE script (no result JSONs).",
    )
    parser.add_argument(
        "--results-root",
        type=Path,
        default=None,
        help="Root containing 01_/02_/03_* output trees (default: tutorials/output).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for comparison plots (default: output/04_summarise_results).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    if args.priors_only:
        summarise(priors_only=True)
        return
    specs = default_run_specs(args.results_root)
    out = args.output_dir if args.output_dir is not None else OUTPUT_DIR
    summarise(run_specs=specs, output_dir=out)


if __name__ == "__main__":
    main()
