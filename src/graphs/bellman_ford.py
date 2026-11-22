"""Bellman-Ford with early exit and negative cycle detection - O(V * E)."""

import math
from typing import Optional
from .graph import Graph

INF = math.inf


def bellman_ford(
    graph: Graph,
    source: int,
    counters: dict | None = None,
) -> tuple[list[float], list[Optional[int]], bool]:
    """Return (dist, prev, has_negative_cycle).

    If has_negative_cycle is True, the dist array is unreliable for affected
    vertices but is still returned for diagnostic purposes.
    """
    V = graph.num_vertices
    dist = [INF] * V
    prev: list[Optional[int]] = [None] * V
    dist[source] = 0.0

    relaxations = 0
    iterations_done = 0

    # build flat edge list once for efficiency
    edges = [(u, v, w) for u, nbrs in enumerate(graph.adj) for v, w in nbrs]

    for iteration in range(V):
        updated = False
        for u, v, w in edges:
            relaxations += 1
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                prev[v] = u
                updated = True
        iterations_done += 1
        if not updated:
            break

    # check for negative cycles: one more pass
    has_negative_cycle = False
    for u, v, w in edges:
        relaxations += 1
        if dist[u] != INF and dist[u] + w < dist[v]:
            has_negative_cycle = True
            break

    if counters is not None:
        counters["relaxations"] = counters.get("relaxations", 0) + relaxations
        counters["iterations"] = counters.get("iterations", 0) + iterations_done

    return dist, prev, has_negative_cycle
