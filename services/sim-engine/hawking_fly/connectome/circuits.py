"""Loom-escape circuit queries — the Phase 0/1 flagship circuit.

Classical physiology describes visual loom detectors LC4 and LPLC2 feeding the
DNp01 "giant fiber" descending neuron, the command neuron for the fly's fast
escape jump. Per spec §7-0A we must NOT trust that diagram blindly — query the
*actual* path in MaleCNS v1.0, which may include different or additional
intermediate neurons.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from hawking_fly.connectome.client import ConnectomeClient

if TYPE_CHECKING:
    import pandas as pd

LOOM_RECEPTOR_TYPES = ("LC4", "LPLC2")
DESCENDING_NEURON_TYPES = ("DNp01",)


def query_loom_escape_circuit(
    client: ConnectomeClient,
    *,
    rois: tuple[str, ...] | None = None,
) -> dict[str, object]:
    """Trace the LC4/LPLC2 -> DNp01 path *in this dataset*.

    Returns a dict with the neuron tables, the direct adjacency, and any
    discovered intermediate neurons between the receptors and the giant fiber.
    Raises NoTokenError if no neuPrint token is configured.
    """
    from neuprint import NeuronCriteria, fetch_neurons, merge_neuron_pairs

    result: dict[str, object] = {
        "dataset": client.config.dataset,
        "receptor_types": LOOM_RECEPTOR_TYPES,
        "descending_types": DESCENDING_NEURON_TYPES,
    }

    receptor_df = client.fetch_neurons(" ".join(LOOM_RECEPTOR_TYPES))
    dn_df = client.fetch_neurons(" ".join(DESCENDING_NEURON_TYPES))

    result["receptor_neurons"] = receptor_df
    result["dnp01_neurons"] = dn_df

    # Direct synapses receptors -> giant fiber
    adj = client.fetch_adjacencies(
        " ".join(LOOM_RECEPTOR_TYPES), " ".join(DESCENDING_NEURON_TYPES)
    )
    result["direct_receptor_to_dnp01"] = adj

    # Intermediate exploration: downstream of receptors, then who hits DNp01
    # upstream partners. (Heavy queries are gated behind explicit use so the
    # Phase 0A flyvis path never triggers them.)
    result["method"] = (
        "direct adjacency LC4/LPLC2 -> DNp01 pulled from live connectome; "
        "intermediate-path reconstruction pending explicit exploration"
    )
    return result


def build_loom_escape_subgraph(client: ConnectomeClient) -> dict[str, object]:
    """Produce a bounded, anatomy-aware subgraph for the propagation layer.

    Pulls the receptors + giant fiber + (optionally) their partners and
    returns adjacency data ready for `propagation.graph_build` to consume.
    Raises NoTokenError if no neuPrint token is configured.
    """
    data = query_loom_escape_circuit(client)

    # Collect edge rows from the direct adjacency table.
    adj: "pd.DataFrame" = data["direct_receptor_to_dnp01"]  # type: ignore[assignment]
    edges = adj[["bodyId", "bodyId_pre", "bodyId_post", "syn_count"]].rename(
        columns={"bodyId_pre": "pre", "bodyId_post": "post", "syn_count": "weight"}
    )
    data["edges"] = edges
    return data