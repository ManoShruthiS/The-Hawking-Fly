"""Tests for the custom propagation RateModel (fast, no flyvis dependency).

Skipped from import cost: these only need numpy/scipy.
"""

import numpy as np
from scipy import sparse

from hawking_fly.propagation.rate_model import RateModel, relu, saturating


def _three_node_unconnected_model():
    return RateModel(weight=sparse.csr_matrix(np.zeros((3, 3))), dt=0.01)


def test_from_edge_list_normalizes_incoming():
    # nodes 0,1,2 ; edges 0->1 (2), 0->2 (2), 1->2 (2)
    # incoming sums: node0=0, node1=2, node2=4
    model = RateModel.from_edge_list(
        pre=[0, 0, 1],
        post=[1, 2, 2],
        weights=[2.0, 2.0, 2.0],
        n_nodes=3,
        dt=0.01,
    )
    w = model.weight.toarray()
    # column-normalized incoming weights
    np.testing.assert_allclose(w.sum(axis=0), [0.0, 1.0, 1.0], atol=1e-12)


def test_step_stays_bounded_and_finite():
    model = _three_node_unconnected_model()
    r = np.array([0.5, 0.5, 0.5])
    out = model.step(r, np.zeros(3))
    assert np.all(np.isfinite(out))


def test_simulate_shape():
    model = RateModel(
        weight=sparse.eye(2).tocsr(), tau=0.05, nonlinearity=relu, dt=0.05
    )
    inputs = np.ones((10, 2))
    trace = model.simulate(np.zeros(2), inputs)
    assert trace.shape == (10, 2)
    assert np.all(np.isfinite(trace))


def test_memory_with_input_propagates():
    # A -> B chain: A input drives B with carry-through latency.
    w = sparse.coo_matrix(([1.0], ([1], [0])), shape=(2, 2)).tocsr()
    model = RateModel(weight=w, tau=0.05, nonlinearity=saturating, dt=0.05)
    inputs = np.zeros((20, 2))
    inputs[:, 0] = 1.0  # A driven high
    trace = model.simulate(np.zeros(2), inputs)
    # B should rise well above its resting 0.
    assert trace[:, 1].max() > 0.5
    assert trace[:, 0].min() >= 0.0


def test_relu_and_saturating_bounds():
    x = np.array([-2.0, 0.0, 2.0])
    assert np.all(relu(x) >= 0.0)
    assert np.all((saturating(x) >= 0.0) & (saturating(x) <= 1.0))