"""Pytest suite for graph algorithms."""

import math
import pytest

from algo_eval.src.graphs.graph import Graph
from algo_eval.src.graphs.dijkstra_heap import dijkstra_heap
from algo_eval.src.graphs.dijkstra_array import dijkstra_array
from algo_eval.src.graphs.bellman_ford import bellman_ford
from algo_eval.src.graphs.spfa import spfa
from algo_eval.src.generators.graphs import make_sparse_grid_graph, make_dense_graph

INF = math.inf


def _simple_graph():
    """Return a small weighted directed graph with known shortest paths from 0."""
    # 0->1 (4), 0->2 (1), 2->1 (2), 1->3 (1), 2->3 (5)
    # Shortest paths from 0: d[0]=0, d[1]=3, d[2]=1, d[3]=4
    g = Graph(4)
    g.add_edge(0, 1, 4)
    g.add_edge(0, 2, 1)
    g.add_edge(2, 1, 2)
    g.add_edge(1, 3, 1)
    g.add_edge(2, 3, 5)
    return g


def _neg_safe_graph():
    """Graph with a negative edge but no negative cycle."""
    # 0->1 (3), 0->2 (5), 1->2 (-2), 2->3 (1)
    # from 0: d[1]=3, d[2]=1, d[3]=2
    g = Graph(4)
    g.add_edge(0, 1, 3)
    g.add_edge(0, 2, 5)
    g.add_edge(1, 2, -2)
    g.add_edge(2, 3, 1)
    return g


def _neg_cycle_graph():
    """Graph containing a negative cycle: 1->2->3->1 total weight -1."""
    g = Graph(4)
    g.add_edge(0, 1, 2)
    g.add_edge(1, 2, -1)
    g.add_edge(2, 3, -1)
    g.add_edge(3, 1, -1)
    return g


class TestDijkstraHeap:
    def test_simple(self):
        g = _simple_graph()
        dist, prev = dijkstra_heap(g, 0)
        assert dist[0] == pytest.approx(0)
        assert dist[1] == pytest.approx(3)
        assert dist[2] == pytest.approx(1)
        assert dist[3] == pytest.approx(4)

    def test_unreachable(self):
        g = Graph(3)
        g.add_edge(0, 1, 5)
        dist, _ = dijkstra_heap(g, 0)
        assert math.isinf(dist[2])

    def test_single_vertex(self):
        g = Graph(1)
        dist, _ = dijkstra_heap(g, 0)
        assert dist[0] == pytest.approx(0)

    def test_neg_weight_behaviour(self):
        """Dijkstra with lazy-deletion heap processes all relaxations including negative-weight edges.

        On acyclic negative-weight graphs it may still find correct answers because the
        lazy heap keeps re-relaxing through updated tentative distances.  The important
        correctness contract is: Dijkstra MUST NOT be used on graphs with negative cycles
        (it infinite-loops), and results on negative-weight sparse graphs must be validated
        against Bellman-Ford in the benchmark.  This test verifies that Dijkstra runs without
        crashing on a graph with negative edges and returns finite distances for reachable nodes.
        """
        g = Graph(3)
        g.add_edge(0, 1, 10)
        g.add_edge(0, 2, 1)
        g.add_edge(2, 1, -3)
        dist_dijkstra, _ = dijkstra_heap(g, 0)
        # Must finish and return finite values for reachable nodes
        assert len(dist_dijkstra) == 3
        assert dist_dijkstra[0] == pytest.approx(0.0)
        assert math.isfinite(dist_dijkstra[1])
        assert math.isfinite(dist_dijkstra[2])

    def test_counters(self):
        g = _simple_graph()
        ctrs = {}
        dijkstra_heap(g, 0, counters=ctrs)
        assert ctrs["heap_pushes"] > 0
        assert ctrs["relaxations"] > 0


class TestDijkstraArray:
    def test_simple(self):
        g = _simple_graph()
        dist, _ = dijkstra_array(g, 0)
        assert dist[1] == pytest.approx(3)
        assert dist[2] == pytest.approx(1)
        assert dist[3] == pytest.approx(4)

    def test_matches_heap_on_positive(self):
        g = make_sparse_grid_graph(5, 5, seed=10, weight_mode="positive")
        d_heap, _ = dijkstra_heap(g, 0)
        d_arr, _ = dijkstra_array(g, 0)
        for a, b in zip(d_heap, d_arr):
            if math.isinf(a) and math.isinf(b):
                continue
            assert abs(a - b) < 1e-6


class TestBellmanFord:
    def test_simple(self):
        g = _simple_graph()
        dist, prev, neg_cycle = bellman_ford(g, 0)
        assert neg_cycle is False
        assert dist[1] == pytest.approx(3)
        assert dist[3] == pytest.approx(4)

    def test_negative_edges_correct(self):
        g = _neg_safe_graph()
        dist, _, neg_cycle = bellman_ford(g, 0)
        assert neg_cycle is False
        assert dist[2] == pytest.approx(1)
        assert dist[3] == pytest.approx(2)

    def test_negative_cycle_detected(self):
        g = _neg_cycle_graph()
        _, _, neg_cycle = bellman_ford(g, 0)
        assert neg_cycle is True

    def test_counters(self):
        g = _simple_graph()
        ctrs = {}
        bellman_ford(g, 0, counters=ctrs)
        assert ctrs["relaxations"] > 0


class TestSPFA:
    def test_simple(self):
        g = _simple_graph()
        dist, _, neg_cycle = spfa(g, 0)
        assert neg_cycle is False
        assert dist[1] == pytest.approx(3)
        assert dist[3] == pytest.approx(4)

    def test_negative_edges_correct(self):
        g = _neg_safe_graph()
        dist, _, neg_cycle = spfa(g, 0)
        assert neg_cycle is False
        assert dist[2] == pytest.approx(1)

    def test_negative_cycle_detected(self):
        g = _neg_cycle_graph()
        _, _, neg_cycle = spfa(g, 0)
        assert neg_cycle is True

    def test_matches_bellman_ford(self):
        # Use a graph with no negative cycle; seed 55 is verified clean
        g = make_sparse_grid_graph(4, 4, seed=55, weight_mode="positive")
        dist_bf, _, _ = bellman_ford(g, 0)
        dist_spfa, _, _ = spfa(g, 0)
        for a, b in zip(dist_bf, dist_spfa):
            if math.isinf(a) and math.isinf(b):
                continue
            assert abs(a - b) < 1e-6, f"BF={a:.4f} SPFA={b:.4f}"


class TestGeneratorDeterminism:
    def test_sparse_same_seed(self):
        g1 = make_sparse_grid_graph(4, 4, seed=42, weight_mode="positive")
        g2 = make_sparse_grid_graph(4, 4, seed=42, weight_mode="positive")
        assert g1.num_edges() == g2.num_edges()

    def test_dense_edges(self):
        g = make_dense_graph(50, seed=1, weight_mode="positive")
        assert g.num_edges() > 50  # dense should have many edges

    def test_negative_cycle_graph_has_neg_weights(self):
        g = make_sparse_grid_graph(5, 5, seed=99, weight_mode="negative_cycle")
        assert g.has_negative_weights()
