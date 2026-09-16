"""Graph construction — build a bounded, anatomy-aware subgraph for the model.

Phase 0A: without a neuPrint token the MaleCNS circuit (LC4/LPLC2 -> DNp01)
cannot be fetched yet, so `build_from_circuit_cache` also accepts synthetic /
cached edge data. Everything here returns a RateModel-ready edge list plus
node metadata.
"""

from __future__ import annotations

import pandas as pd

from hawking_fly.connectome.cache import load_cached_circuit, list_cached_circuits
from hawking_fly.connectome.client import NoTokenError


def circuit_to_edges(
    circuit_data: dict[str, object],
) -> tuple[pd.DataFrame, dict[str, str]]:
    """Extract an edge frame + metadata from a connectome circuit pull."""
    if "edges" not in circuit_data:
        raise ValueError("circuit_data has no 'edges' — run build_loom_escape_subgraph first.")
    edges: pd.DataFrame = circuit_data["edges"]  # type: ignore[assignment]
    meta = {
        "dataset": str(circuit_data.get("dataset", "unknown")),
        "method": str(circuit_data.get("method", "")),
    }
    return edges, meta


def build_from_cache(
    name: str,
) -> tuple[pd.DataFrame | None, dict[str, str]]:
    """Load a cached circuit snapshot (or explain why there is none)."""
    edges, info = load_cached_circuit(name)
    if edges is None:
        available = list_cached_circuits()
        raise NoTokenError(
            f"No cached circuit '{name}'. Connectome fetch required — add a "
            "NEUPRINT_TOKEN to .env. Available caches: "
            + (", ".join(available) if available else "none")
        )
    meta = {"dataset": info.dataset, "cached_at": info.created}
    return edges, meta