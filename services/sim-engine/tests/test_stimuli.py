"""Tests for the sensory stimuli (loom rendering; needs flyvis import)."""

import numpy as np
import pytest

from hawking_fly.sensory.stimuli import Loom, build_loom


def test_loom_build_shape_and_range():
    frames = build_loom(t_pre=0.2, t_stim=0.2, t_hold=0.1, t_post=0.2, dt=0.01)
    assert frames.ndim == 2
    assert frames.shape[1] == BoxEye_hexals()
    assert np.all((frames >= 0.0) & (frames <= 1.0))


def test_loom_expands_monotonically():
    # Number of active (bright) hexals should grow during the grow phase.
    frames = build_loom(
        t_pre=0.1, t_stim=0.5, t_hold=0.1, t_post=0.1, dt=0.05, baseline=0.5, intensity=1.0,
        start_radius=0, end_radius=8,
    )
    grow = frames[int(0.1/0.05):int(0.6/0.05)]
    counts = [int(np.sum(f > 0.75)) for f in grow]
    deltas = np.diff(np.array(counts, dtype=float))
    assert np.all(deltas >= 0), "loom area should be monotonic non-decreasing"


def test_loom_dataset_len_and_item():
    ds = Loom(intensities=[1.0, 0.0], dt=0.01)
    assert len(ds) == 2
    item = ds[0]
    assert item.ndim == 2
    assert item.shape[1] == BoxEye_hexals()
    assert item.shape[0] > 0


def BoxEye_hexals() -> int:
    from flyvis.datasets.rendering import BoxEye

    return BoxEye(extent=15, kernel_size=13).hexals