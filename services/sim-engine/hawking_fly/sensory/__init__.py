"""Sensory encoding layer — synthetic stimuli and the pretrained flyvis vision model."""
from hawking_fly.sensory.stimuli import Loom, STIMULI, STIMULUS_CLASSES
from hawking_fly.sensory.flyvis_wrapper import (
    FlyVisWrapper,
    ensure_pretrained_ensemble,
    pretrained_network_dir,
)

__all__ = [
    "Loom",
    "STIMULI",
    "STIMULUS_CLASSES",
    "FlyVisWrapper",
    "ensure_pretrained_ensemble",
    "pretrained_network_dir",
]