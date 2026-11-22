"""Generator for synthetic road-network graphs (Islamabad/Rawalpindi city model)."""

import random
import math
from ..graphs.graph import Graph


def _apply_potential_reweighting(g: Graph, rng: random.Random) -> None:
    """Use potential-based reweighting to guarantee negative edges without negative cycles.

    Assigns potentials h(u) such that w'(u,v) = w(u,v) + h(u) - h(v).
    Any cycle sum remains identical to the original strictly positive sum.
    """
    V = g.num_vertices
    h = [round(rng.uniform(0.0, 10.0), 2) for _ in range(V)]
    new_adj = [[] for _ in range(V)]
    for u in range(V):
        for v, w in g.adj[u]:
            new_w = round(w + h[u] - h[v], 2)
            new_adj[u].append((v, new_w))
    g.adj = new_adj


def make_sparse_grid_graph(
    rows: int,
    cols: int,
    seed: int,
    weight_mode: str = "positive",
) -> Graph:
    """Grid graph where each cell is an intersection; roads connect adjacent cells.

    Sparse: each node connects to adjacent cells plus a few shortcut edges (~3-5 E/V).
    weight_mode: 'positive', 'negative_safe', 'negative_cycle'
    """
    rng = random.Random(seed)
    V = rows * cols
    g = Graph(V)

    def node(r, c):
        return r * cols + c

    for r in range(rows):
        for c in range(cols):
            u = node(r, c)
            if c + 1 < cols:
                w = round(rng.uniform(2.0, 15.0), 2)
                g.add_undirected_edge(u, node(r, c + 1), w)
            if r + 1 < rows:
                w = round(rng.uniform(2.0, 15.0), 2)
                g.add_undirected_edge(u, node(r + 1, c), w)

    num_shortcuts = max(1, V // 20)
    for _ in range(num_shortcuts):
        u = rng.randrange(V)
        v = rng.randrange(V)
        if u != v:
            w = round(rng.uniform(5.0, 30.0), 2)
            g.add_edge(u, v, w)

    if weight_mode in ("negative_safe", "negative_cycle"):
        _apply_potential_reweighting(g, rng)

    if weight_mode == "negative_cycle":
        _inject_negative_cycle(g, rng, V)

    return g


def make_dense_graph(
    V: int,
    seed: int,
    weight_mode: str = "positive",
) -> Graph:
    """Dense directed graph with ~V^2/4 edges (every vertex connects to ~V/2 others)."""
    rng = random.Random(seed)
    g = Graph(V)
    for u in range(V):
        targets = rng.sample(range(V), k=max(1, V // 2))
        for v in targets:
            if v != u:
                w = round(rng.uniform(2.0, 20.0), 2)
                g.add_edge(u, v, w)

    if weight_mode in ("negative_safe", "negative_cycle"):
        _apply_potential_reweighting(g, rng)

    if weight_mode == "negative_cycle":
        _inject_negative_cycle(g, rng, V)

    return g


def _inject_negative_cycle(g: Graph, rng: random.Random, V: int) -> None:
    """Add a small directed negative-weight cycle (3 nodes) for detection tests."""
    if V < 3:
        return
    a, b, c = rng.sample(range(V), 3)
    g.add_edge(a, b, -10.0)
    g.add_edge(b, c, -10.0)
    g.add_edge(c, a, -10.0)


def graph_sizes_sparse() -> list[tuple[int, int]]:
    """Return (rows, cols) pairs giving target vertex counts for sparse graphs."""
    targets = [100, 500, 1000, 5000, 10000]
    result = []
    for t in targets:
        side = int(math.isqrt(t))
        result.append((side, side))
    return result


def graph_sizes_dense() -> list[int]:
    """Return vertex counts for dense graph experiments."""
    return [100, 500, 1000, 5000]


WEIGHT_MODES = ["positive", "negative_safe", "negative_cycle"]
