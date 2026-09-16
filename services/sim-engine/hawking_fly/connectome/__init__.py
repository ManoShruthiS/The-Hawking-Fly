"""Connectome data layer — fetch, cache, and expose queryable fly connectivity graphs."""
from hawking_fly.connectome.config import ConnectomeConfig, get_config
from hawking_fly.connectome.client import ConnectomeClient, NoTokenError
from hawking_fly.connectome.circuits import query_loom_escape_circuit
from hawking_fly.connectome.cache import load_cached_circuit, save_circuit_cache

__all__ = [
    "ConnectomeConfig",
    "get_config",
    "ConnectomeClient",
    "NoTokenError",
    "query_loom_escape_circuit",
    "load_cached_circuit",
    "save_circuit_cache",
]