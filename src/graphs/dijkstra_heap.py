"""Dijkstra with binary heap (lazy deletion via heapq) - O((V + E) log V)."""

import heapq
import math
from typing import Optional
from .graph import Graph

INF = math.inf


def dijkstra_heap(
    graph: Graph,
    source: int,
    counters: dict | None = None,
) -> tuple[list[float], list[Optional[int]]]:
    """Return (dist, prev) arrays; prev[v] is the predecessor of v on the shortest path.

    Skips negative-weight graphs but still runs and returns whatever answer it
    produces (which may be wrong) so callers can record the failure.
    """
    V = graph.num_vertices
    dist = [INF] * V
    prev: list[Optional[int]] = [None] * V
    dist[source] = 0.0

    heap = [(0.0, source)]
    pushes = 0
    pops = 0
    relaxations = 0
    max_pops = 5 * (V + graph.num_edges() + 1)

    while heap:
        d, u = heapq.heappop(heap)
        pops += 1
        if pops > max_pops:
            break
        if d > dist[u]:
            continue
        for v, w in graph.adj[u]:
            relaxations += 1
            nd = dist[u] + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, v))
                pushes += 1

    if counters is not None:
        counters["heap_pushes"] = counters.get("heap_pushes", 0) + pushes
        counters["heap_pops"] = counters.get("heap_pops", 0) + pops
        counters["relaxations"] = counters.get("relaxations", 0) + relaxations

    return dist, prev
