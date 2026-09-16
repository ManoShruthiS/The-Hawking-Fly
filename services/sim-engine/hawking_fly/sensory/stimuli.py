"""Sensory encoding layer — synthetic "world events" as activation patterns.

Phase 0A uses three stimuli: flash, moving edge, and loom. Flash and moving
edge use flyvis's native datasets. Loom (an expanding dark/bright disk, the
canonical predator-approach stimulus for the LC4/LPLC2 -> DNp01 escape
pathway) is rendered here on the same hexagonal receptor lattice flyvis uses.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import torch
from flyvis.datasets.datasets import SequenceDataset
from flyvis.datasets.flashes import Flashes
from flyvis.datasets.moving_bar import MovingEdge
from flyvis.datasets.rendering import BoxEye
from flyvis.utils.hex_utils import HexLattice
from flyvis.utils.hex_utils import Hexal

STIMULI = ("flash", "moving_edge", "loom")


def build_loom(
    *,
    boxfilter: dict = dict(extent=15, kernel_size=13),
    baseline: float = 0.5,
    intensity: float = 1.0,
    t_pre: float = 1.0,
    t_stim: float = 1.0,
    t_hold: float = 0.5,
    t_post: float = 1.0,
    dt: float = 1 / 200,
    start_radius: int = 0,
    end_radius: int = 15,
) -> np.ndarray:
    """Render a looming disk on the hexagonal receptor lattice.

    An expanding circle on a hexagonal grid, matching how flyvis renders flash
    frames (per-ommatidium intensity array). Contrast *intensity* against
    *baseline* (e.g. dark 0.0 or bright 1.0 vs mid-grey 0.5).

    Returns an array of shape (frames, n_ommatidia).
    """
    box = BoxEye(**boxfilter)
    n_ommatidia = box.hexals
    grey = np.full((1, n_ommatidia), baseline)

    radii = np.linspace(start_radius, end_radius, int(round(t_stim / dt)) + 1)

    def _disk(r: float) -> np.ndarray:
        frame = grey.copy()
        ring = HexLattice.filled_circle(
            radius=int(round(r)), center=Hexal(0, 0, 0), as_lattice=True
        )
        idx = np.asarray(ring.where(1))
        frame[:, idx] = intensity
        return frame

    grow = np.concatenate([_disk(float(r)) for r in radii[:-1]], axis=0)
    hold = np.repeat(_disk(float(end_radius)), int(round(t_hold / dt)), axis=0)

    pre = np.repeat(grey, int(round(t_pre / dt)), axis=0)
    post = np.repeat(grey, int(round(t_post / dt)), axis=0)

    return np.concatenate([pre, grow, hold, post], axis=0)


class Loom(SequenceDataset):
    """Looming-stimulus dataset compatible with flyvis NetworkView responses."""

    arg_df: pd.DataFrame | None = None

    def __init__(
        self,
        boxfilter: dict = dict(extent=15, kernel_size=13),
        baseline: float = 0.5,
        intensities: list[float] = (1.0,),
        t_pre: float = 1.0,
        t_stim: float = 1.0,
        t_hold: float = 0.5,
        t_post: float = 1.0,
        dt: float = 1 / 200,
        start_radius: int = 0,
        end_radius: int = 15,
    ) -> None:
        self.boxfilter = boxfilter
        self.baseline = baseline
        self.intensities = list(intensities)
        self.t_pre = t_pre
        self.t_stim = t_stim
        self.t_hold = t_hold
        self.t_post = t_post
        self.dt = dt
        self.start_radius = start_radius
        self.end_radius = end_radius
        self.arg_df = pd.DataFrame(
            {
                "baseline": [self.baseline] * len(self.intensities),
                "intensity": list(self.intensities),
            }
        )

    @property
    def t_post(self) -> float:  # type: ignore[override]
        # SequenceDataset declares t_post as a class attr; expose instance value.
        return self._t_post

    @t_post.setter
    def t_post(self, value: float) -> None:
        self._t_post = value

    def get_item(self, key: int) -> torch.Tensor:
        intensity = self.intensities[key]
        frames = build_loom(
            boxfilter=self.boxfilter,
            baseline=self.baseline,
            intensity=float(intensity),
            t_pre=self.t_pre,
            t_stim=self.t_stim,
            t_hold=self.t_hold,
            t_post=self.t_post,
            dt=self.dt,
            start_radius=self.start_radius,
            end_radius=self.end_radius,
        )
        return torch.Tensor(frames)

    def __len__(self) -> int:
        return len(self.intensities)

    def __repr__(self) -> str:
        return f"Loom dataset: {self.arg_df.to_dict('records')}"


STIMULUS_CLASSES: dict[str, type] = {
    "flash": Flashes,
    "moving_edge": MovingEdge,
    "loom": Loom,
}