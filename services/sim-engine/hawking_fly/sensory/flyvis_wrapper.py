"""flyvis wrapper — the one fully pretrained component.

flyvis (Lappalainen et al. 2024) is a connectome-constrained network of the
fly's optic lobe, validated against real recordings. Phase 0A uses only its
forward inference on synthetic stimuli; training flyvis from scratch is out of
scope (and the M5 Air would throttle on it anyway).

The pretrained ensemble `flow/0000/000` is downloaded from flyvis's Google
Drive distribution on first use (`flyvis download-pretrained --skip_large_files`).
"""

from __future__ import annotations

import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import xarray as xr

from flyvis import NetworkView, results_dir
from flyvis.datasets.flashes import Flashes
from flyvis.datasets.moving_bar import MovingEdge

from hawking_fly.sensory.stimuli import Loom

logger = logging.getLogger(__name__)

FLOW_NETWORK = Path("flow/0000/000")


def pretrained_network_dir() -> Path:
    return results_dir / FLOW_NETWORK


def ensure_pretrained_ensemble(download: bool = False) -> Path:
    """Return the path to the pretrained flyvis network, downloading if needed.

    Raises RuntimeError with instructions (instead of silently downloading GBs)
    unless download=True, or if the download CLI is unavailable.
    """
    network_dir = pretrained_network_dir()
    if network_dir.exists():
        return network_dir

    if not download:
        raise RuntimeError(
            "Pretrained flyvis ensemble not found at "
            f"{network_dir}. Run `flyvis download-pretrained --skip_large_files` "
            "(one-time, ~1 GB) or call ensure_pretrained_ensemble(download=True)."
        )

    cli = shutil.which("flyvis")
    if cli is None:
        cli_cmd = [sys.executable, "-m", "flyvis_cli.flyvis_cli"]
    else:
        cli_cmd = [cli]
    logger.info("Downloading pretrained flyvis ensemble (one-time).")
    subprocess.run(
        [*cli_cmd, "download-pretrained", "--skip_large_files"],
        check=True,
    )
    if not network_dir.exists():
        raise RuntimeError("flyvis download reported success but the network dir is missing.")
    return network_dir


class FlyVisWrapper:
    """Load the pretrained optic-lobe network and run synthetic stimuli.

    Responses are returned as xarray Datasets from flyvis, so downstream code
    (propagation layer, notebook, plots) can slice by `cell_type`, `time`, and
    stimulus coordinates. This keeps the flyvis-specific surface small.
    """

    def __init__(self, network_reldir: str | Path = FLOW_NETWORK) -> None:
        self.network_dir = results_dir / network_reldir
        self.network_view: NetworkView | None = None

    def _view(self) -> NetworkView:
        if self.network_view is None:
            self.network_view = NetworkView(self.network_dir)
        return self.network_view

    def responses(self, stimulus: str, **cfg: Any) -> xr.Dataset:
        """Run one stimulus and return the response xarray Dataset."""
        if stimulus == "flash":
            dataset = Flashes(
                dynamic_range=cfg.get("dynamic_range", [0, 1]),
                t_stim=cfg.get("t_stim", 1.0),
                t_pre=cfg.get("t_pre", 1.0),
                dt=cfg.get("dt", 1 / 200),
                radius=cfg.get("radius", [-1, 6]),
                alternations=cfg.get("alternations", (0, 1, 0)),
            )
            return self._view().flash_responses(dataset=dataset)
        if stimulus == "moving_edge":
            dataset = MovingEdge(
                widths=cfg.get("widths", [2]),
                offsets=cfg.get("offsets", (-5, 6)),
                intensities=cfg.get("intensities", [0, 1]),
                speeds=cfg.get("speeds", [13]),
                angles=cfg.get("angles", [0]),
                t_pre=cfg.get("t_pre", 1.0),
                t_post=cfg.get("t_post", 1.0),
                dt=cfg.get("dt", 1 / 200),
            )
            return self._view().moving_edge_responses(dataset=dataset)
        if stimulus == "loom":
            dataset = Loom(
                intensities=cfg.get("intensities", [1.0, 0.0]),
                baseline=cfg.get("baseline", 0.5),
                t_pre=cfg.get("t_pre", 1.0),
                t_stim=cfg.get("t_stim", 1.0),
                t_hold=cfg.get("t_hold", 0.5),
                t_post=cfg.get("t_post", 1.0),
                dt=cfg.get("dt", 1 / 200),
                start_radius=cfg.get("start_radius", 0),
                end_radius=cfg.get("end_radius", 15),
            )
            from flyvis.analysis.stimulus_responses import generic_responses

            return generic_responses(
                self._view(),
                dataset=None,
                dataset_config={
                    "intensities": dataset.intensities,
                    "baseline": dataset.baseline,
                    "t_pre": dataset.t_pre,
                    "t_stim": dataset.t_stim,
                    "t_hold": dataset.t_hold,
                    "t_post": dataset.t_post,
                    "dt": dataset.dt,
                    "start_radius": dataset.start_radius,
                    "end_radius": dataset.end_radius,
                },
                default_dataset_cls=Loom,
                t_pre=1.0,
                t_fade_in=0.0,
                batch_size=cfg.get("batch_size", 1),
            )
        raise ValueError(f"Unknown stimulus '{stimulus}'. Choose from flash, moving_edge, loom.")