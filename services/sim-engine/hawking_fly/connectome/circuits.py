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


def _receptor_criteria():
    from neuprint import NeuronCriteria

    return NeuronCriteria(type=list(LOOM_RECEPTOR_TYPES))


def _dn_criteria():
    from neuprint import NeuronCriteria

    return NeuronCriteria(type=list(DESCENDING_NEURON_TYPES))


def query_loom_escape_circuit(
    client: ConnectomeClient,
    *,
    rois: tuple[str, ...] | None = None,
) -> dict[str, object]:
    """Trace the LC4/LPLC2 -> DNp01 path *in this dataset*.

    Returns a dict with the neuron tables, the direct adjacency edges, and any
    discovered intermediate neurons between the receptors and the giant fiber.
    Raises NoTokenError if no neuPrint token is configured.
    """
    result: dict[str, object] = {
        "dataset": client.config.dataset,
        "receptor_types": LOOM_RECEPTOR_TYPES,
        "descending_types": DESCENDING_NEURON_TYPES,
    }

    receptor_df, _ = client.fetch_neurons(_receptor_criteria())
    dn_df, _ = client.fetch_neurons(_dn_criteria())

    result["receptor_neurons"] = receptor_df
    result["dnp01_neurons"] = dn_df

    # Direct synapses receptors -> giant fiber
    sources_df, edges_df = client.fetch_adjacencies(_receptor_criteria(), _dn_criteria())
    result["direct_receptor_to_dnp01_neurons"] = sources_df
    result["direct_receptor_to_dnp01_edges"] = edges_df

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
    returns edge data ready for `propagation.graph_build` to consume.
    Raises NoTokenError if no neuPrint token is configured.
    """
    data = query_loom_escape_circuit(client)

    # Collect edge rows from the direct adjacency edges table.
    edge_df: "pd.DataFrame" = data["direct_receptor_to_dnp01_edges"]  # type: ignore[assignment]
    edges = edge_df.rename(
        columns={
            "bodyId_pre": "pre",
            "bodyId_post": "post",
            "weight": "syn_count",
        }
    )
    data["edges"] = edges
    return data