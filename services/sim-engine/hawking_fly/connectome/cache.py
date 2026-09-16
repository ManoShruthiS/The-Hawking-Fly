"""Snapshot connectome pulls to local storage so runtime never re-queries live APIs.

Cached circuit data lives under ``data/connectome/`` (gitignored). A cache
entry stores the adjacency DataFrame plus metadata (dataset, timestamp) so a
result is always traceable to a snapshot.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

CACHE_DIR = Path(__file__).resolve().parents[3] / "data" / "connectome"


@dataclass
class CircuitCacheInfo:
    path: Path
    dataset: str
    created: str


def _meta_path(circuit_path: Path) -> Path:
    return circuit_path.with_suffix(".json")


def save_circuit_cache(
    name: str,
    edges: pd.DataFrame,
    dataset: str,
    extra: dict | None = None,
) -> Path:
    """Write an adjacency snapshot (parquet) + metadata (json) to the cache dir."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    circuit_path = CACHE_DIR / f"{name}.circuit.parquet"
    edges.to_parquet(circuit_path, index=False)

    created = datetime.now(timezone.utc).isoformat()
    meta = {"dataset": dataset, "created": created, "notes": extra or {}}
    _meta_path(circuit_path).write_text(json.dumps(meta, indent=2, default=str))
    return circuit_path


def load_cached_circuit(name: str) -> tuple[pd.DataFrame | None, CircuitCacheInfo | None]:
    """Load a cached circuit snapshot; returns (edges_df, info) or (None, None)."""
    circuit_path = CACHE_DIR / f"{name}.circuit.parquet"
    if not circuit_path.exists():
        return None, None

    meta = json.loads(_meta_path(circuit_path).read_text())
    edges = pd.read_parquet(circuit_path)
    info = CircuitCacheInfo(
        path=circuit_path,
        dataset=meta["dataset"],
        created=meta["created"],
    )
    return edges, info


def list_cached_circuits() -> list[str]:
    """Names of cached circuit snapshots (without suffixes)."""
    return sorted(p.name.removesuffix(".circuit.parquet") for p in CACHE_DIR.glob("*.parquet"))