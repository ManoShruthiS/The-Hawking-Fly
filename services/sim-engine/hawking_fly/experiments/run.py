"""Reproducible Phase 0A experiment runner.

Usage:
    python -m hawking_fly.experiments.run [--config experiments/loom_escape/config.json]

Each run writes an output directory containing:
    config.json            the exact config used
    metrics.json           sanity metrics for this run
    stimuli_responses.npz  stimulus+response arrays
    plots/                 response figure(s)
"""

from __future__ import annotations

import argparse
import json
import logging
import time
from pathlib import Path
from typing import Any

import numpy as np
import xarray as xr

from hawking_fly.sensory import FlyVisWrapper, ensure_pretrained_ensemble
from hawking_fly.sensory.stimuli import STIMULI

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("hawking_fly.experiments.run")

REPO_ROOT = Path(__file__).resolve().parents[4]  # services/sim-engine/hawking_fly/experiments → repo root
DEFAULT_CONFIG = Path("experiments/loom_escape/config.json")


def _responses_to_npz(resp: xr.Dataset, path: Path) -> dict[str, Any]:
    """Dump a flyvis response Dataset to a compact npz + return summary arrays."""
    path.parent.mkdir(parents=True, exist_ok=True)

    responses = None
    if "responses" in resp:
        responses = np.asarray(resp["responses"].values)
    stimulus = None
    if "stimulus" in resp:
        stimulus = np.asarray(resp["stimulus"].values)

    try:
        import xarray as _xr

        coords: dict[str, Any] = {}
        for name, da in resp.coords.items():
            values = np.asarray(da.values)
            if values.ndim == 0:
                coords[name] = str(values.item()) if values.dtype.kind == "O" else values.item()
            else:
                coords[name] = values
    except Exception:  # pragma: no cover
        coords = {}

    with open(path, "wb") as f:
        np.savez(f, responses=responses, stimulus=stimulus)
    return coords


def _summary_metrics(stimuli_responses: dict[str, tuple[np.ndarray, Any]]) -> dict[str, Any]:
    """Compute Phase 0A sanity metrics — not decodability metrics."""
    metrics: dict[str, Any] = {}
    signatures: dict[str, float] = {}

    baseline_traces: dict[str, np.ndarray] = {}
    for name, (responses, _coords) in stimuli_responses.items():
        if responses is None:
            metrics[name] = {"status": "no_response_data"}
            continue
        finite = bool(np.all(np.isfinite(responses)))
        mean_abs = float(np.mean(np.abs(responses)))
        std = float(np.std(responses))
        metrics[name] = {
            "finite": finite,
            "shape": list(responses.shape),
            "mean_abs_response": round(mean_abs, 6),
            "std_response": round(std, 6),
        }
        # mean activity over time across samples & central neurons -> trace
        # responses shape from flyvis: (network_id, sample, frame, neuron)
        if responses.ndim == 4:
            trace = responses[0].mean(axis=(0, -1))
        else:
            trace = responses.reshape(responses.shape[0], -1).mean(axis=1)
        baseline_traces[name] = trace
        signatures[name] = float(np.linalg.norm(trace))

    # Pairwise dissimilarity of mean-response traces (distinguishable?).
    names = list(baseline_traces)
    pairwise: dict[str, float] = {}
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            ta, tb = baseline_traces[a], baseline_traces[b]
            min_len = min(len(ta), len(tb))
            ta, tb = ta[:min_len], tb[:min_len]
            dist = float(np.mean((ta - tb) ** 2)) if min_len else 0.0
            pairwise[f"{a}_vs_{b}_mse"] = round(dist, 8)
    metrics["pairwise_trace_mse"] = pairwise
    metrics["signature_norms"] = {k: round(v, 6) for k, v in signatures.items()}
    return metrics


def run_experiment(config: dict[str, Any]) -> Path:
    sim = config.get("sim", {})
    stimuli_cfg = config.get("stimuli", [])

    seed = int(config.get("seed", 0))
    np.random.seed(seed)

    out_root = REPO_ROOT / sim.get("output_root", "experiments")
    run_dir = out_root / sim.get("experiment", "run") / time.strftime("%Y%m%d-%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "plots").mkdir(exist_ok=True)

    # Ground truth injected into metrics so the run is self-describing.
    provenance = {
        "seed": seed,
        "experiment": sim.get("experiment"),
        "flyvis_pretrained_used": sim.get("use_pretrained", True),
        "neuprint_circuit_status": "pending_token"
        if sim.get("await_token", False)
        else "not_configured",
        "labels": "flyvis forward responses on synthetic stimuli; no decoder claims.",
    }

    logger.info("Ensuring pretrained flyvis ensemble.")
    ensure_pretrained_ensemble(download=bool(sim.get("download_pretrained", False)))

    wrapper = FlyVisWrapper()
    stimuli_responses: dict[str, Any] = {}
    for s in stimuli_cfg:
        name = s["name"]
        if name not in STIMULI:
            logger.warning("Unknown stimulus %s — skipped.", name)
            continue
        logger.info("Running %s.", name)
        resp = wrapper.responses(name, **s.get("cfg", {}))
        coords = _responses_to_npz(resp, run_dir / f"{name}_responses.npz")
        stimuli_responses[name] = (resp.get("responses"), coords)

    metrics = _summary_metrics(stimuli_responses)
    metrics["provenance"] = provenance

    (run_dir / "config.json").write_text(json.dumps(config, indent=2))
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))

    _write_plots(stimuli_responses, run_dir / "plots")

    logger.info("Run complete -> %s", run_dir)
    return run_dir


def _write_plots(stimuli_responses: dict[str, Any], plot_dir: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 4))
    for name, (responses, _coords) in stimuli_responses.items():
        if responses is None:
            continue
        trace = (
            responses[0].mean(axis=(0, -1)) if responses.ndim == 4 else responses.mean(axis=1)
        )
        ax.plot(trace, label=name)
    ax.set_xlabel("frame")
    ax.set_ylabel("mean response (arb. units)")
    ax.set_title("Phase 0A — mean optic-lobe response per stimulus")
    ax.legend()
    fig.tight_layout()
    fig.savefig(plot_dir / "responses_overview.png", dpi=110)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args()

    config_path = args.config
    if not config_path.is_absolute():
        config_path = REPO_ROOT / config_path
    if not config_path.exists():
        logger.error("Config not found: %s", config_path)
        return 1

    config: dict[str, Any] = json.loads(config_path.read_text())
    run_experiment(config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())