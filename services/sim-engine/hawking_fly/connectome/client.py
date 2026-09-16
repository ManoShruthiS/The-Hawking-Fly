"""neuPrint/MaleCNS client — token-driven, fails gracefully without a token.

Phase 0A runs flyvis-only validation until the user adds `NEUPRINT_TOKEN` to
`.env`. Every call that needs neuPrint raises `NoTokenError` instead of
blocking the flyvis-first boot path.

Return shapes follow neuprint-python 0.6.x:
  * fetch_neurons -> (neurons_df, criteria)
  * fetch_adjacencies -> (sources_df, edges_df) with edges columns
    bodyId_pre / bodyId_post / roi / weight
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from hawking_fly.connectome.config import ConnectomeConfig, get_config

if TYPE_CHECKING:
    import pandas as pd


class NoTokenError(RuntimeError):
    """Raised when a neuPrint query is attempted without a configured token."""


class ConnectomeClient:
    """Thin wrapper around neuprint.Client for the primary MaleCNS dataset."""

    def __init__(self, config: ConnectomeConfig | None = None) -> None:
        self.config = config or get_config()
        self._client: Any = None

    @property
    def client(self) -> Any:
        """Lazily construct the neuprint Client once a token is available."""
        if not self.config.has_token:
            raise NoTokenError(
                "No NEUPRINT_TOKEN set. Add a free token from "
                "https://neuprint.janelia.org to a `.env` file at the repo "
                "root (see .env.example). Phase 0A runs flyvis-only until then."
            )
        if self._client is None:
            from neuprint import Client

            self._client = Client(
                self.config.server,
                dataset=self.config.dataset,
                token=self.config.token,
            )
        return self._client

    def fetch_neurons(self, query: Any) -> tuple["pd.DataFrame", Any]:
        """Fetch neurons by type query (e.g. 'DNp01', 'LC4', 'LPLC2').

        `query` may be a plain string or a `neuprint.NeuronCriteria`.
        Returns the neuprint tuple (neurons_df, criteria/details).
        """
        from neuprint import fetch_neurons

        return fetch_neurons(query, client=self.client)

    def fetch_adjacencies(self, source: Any, target: Any) -> tuple["pd.DataFrame", "pd.DataFrame"]:
        """Fetch synapse adjacency between two neuron criteria.

        Returns the neuprint tuple (sources_df, edges_df); the edges frame has
        columns bodyId_pre / bodyId_post / roi / weight.
        """
        from neuprint import fetch_adjacencies

        return fetch_adjacencies(source, target, client=self.client)

    def find_connections(
        self,
        source: Any,
        target: Any,
        min_synapses: int = 1,
    ) -> "pd.DataFrame":
        """Return a table of connections between two sets of cell types."""
        from neuprint import fetch_simple_connections

        return fetch_simple_connections(
            source, target, min_synapses=min_synapses, client=self.client
        )

    def neuron_skeletons(
        self,
        query: str,
        format: str = "neuron",
        *,
        soma: bool = False,
    ) -> list[Any]:
        """Fetch 3D neuron skeletons (neurites/soma) for neural-camera views.

        Requires `navis`. Returns navis Neuron/NeuronList objects.
        """
        from navis.interfaces.neuprint import fetch_neurons as navis_fetch

        return navis_fetch(
            query,
            dataset=self.config.dataset,
            client=self.client,
            format=format,
            soma=soma,
        )