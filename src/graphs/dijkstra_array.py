"""Dijkstra with plain array - O(V^2), better than heap on very dense graphs."""

import math
from typing import Optional
from .graph import Graph

INF = math.inf


def dijkstra_array(
    graph: Graph,
    source: int,
    counters: dict | None = None,
) -> tuple[list[float], list[Optional[int]]]:
    """Return (dist, prev) arrays using the O(V^2) array-based Dijkstra."""
    V = graph.num_vertices
    dist = [INF] * V
    prev: list[Optional[int]] = [None] * V
    visited = [False] * V
    dist[source] = 0.0

    comparisons = 0
    relaxations = 0

    for _ in range(V):
        # find unvisited vertex with minimum distance
        u = -1
        for i in range(V):
            comparisons += 1
            if not visited[i] and (u == -1 or dist[i] < dist[u]):
                u = i
        if u == -1 or dist[u] == INF:
            break
        visited[u] = True
        for v, w in graph.adj[u]:
            relaxations += 1
            nd = dist[u] + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u

    if counters is not None:
        counters["comparisons"] = counters.get("comparisons", 0) + comparisons
        counters["relaxations"] = counters.get("relaxations", 0) + relaxations

    return dist, prev
