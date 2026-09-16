"""Tests for connectome client + cache (no network access, no token)."""

import numpy as np
import pandas as pd

from hawking_fly.connectome.cache import (
    save_circuit_cache,
    load_cached_circuit,
    list_cached_circuits,
)
from hawking_fly.connectome.client import ConnectomeClient, NoTokenError
from hawking_fly.connectome.config import ConnectomeConfig


def test_client_requires_token():
    client = ConnectomeClient(config=ConnectomeConfig(token=None, dataset="male-cns:v1.0"))
    try:
        client.client  # property access raises if no token
    except NoTokenError:
        pass
    else:
        raise AssertionError("expected NoTokenError without a token")


def test_client_with_token_uses_dataset():
    client = ConnectomeClient(
        config=ConnectomeConfig(token="abc", dataset="male-cns:v1.0")
    )
    assert client.config.has_token
    assert client.config.dataset == "male-cns:v1.0"


def test_save_load_roundtrip(tmp_path, monkeypatch):
    from hawking_fly.connectome import cache as cache_mod

    monkeypatch.setattr(cache_mod, "CACHE_DIR", tmp_path)
    edges = pd.DataFrame(
        {"pre": [1, 2, 3], "post": [2, 3, 1], "weight": [5.0, 3.0, 2.0]}
    )
    path = save_circuit_cache("test_circuit", edges, "male-cns:v1.0")
    assert path.exists()

    loaded, info = load_cached_circuit("test_circuit")
    assert loaded is not None
    assert info is not None and info.dataset == "male-cns:v1.0"
    np.testing.assert_array_equal(loaded["weight"].values, [5.0, 3.0, 2.0])
    assert "test_circuit" in list_cached_circuits()


def test_load_missing_circuit(tmp_path, monkeypatch):
    from hawking_fly.connectome import cache as cache_mod

    monkeypatch.setattr(cache_mod, "CACHE_DIR", tmp_path)
    assert load_cached_circuit("nope") == (None, None)