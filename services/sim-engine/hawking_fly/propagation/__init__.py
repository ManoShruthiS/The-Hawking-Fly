"""Propagation layer — custom neural dynamics over the connectome graph."""
from hawking_fly.propagation.rate_model import RateModel, relu, saturating
from hawking_fly.propagation.graph_build import build_from_cache, circuit_to_edges

__all__ = ["RateModel", "relu", "saturating", "build_from_cache", "circuit_to_edges"]