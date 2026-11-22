"""SPFA (Shortest Path Faster Algorithm) - Bellman-Ford with queue optimisation."""

import math
import collections
from typing import Optional
from .graph import Graph

INF = math.inf


def spfa(
    graph: Graph,
    source: int,
    counters: dict | None = None,
) -> tuple[list[float], list[Optional[int]], bool]:
    """Return (dist, prev, has_negative_cycle) using SPFA.

    Negative cycle detection uses the enqueue-count heuristic: if a vertex is
    enqueued more than V times, a negative cycle is reachable from it.
    """
    V = graph.num_vertices
    dist = [INF] * V
    prev: list[Optional[int]] = [None] * V
    in_queue = [False] * V
    enqueue_count = [0] * V
    dist[source] = 0.0

    queue: collections.deque[int] = collections.deque()
    queue.append(source)
    in_queue[source] = True
    enqueue_count[source] = 1

    relaxations = 0
    has_negative_cycle = False

    while queue:
        u = queue.popleft()
        in_queue[u] = False
        for v, w in graph.adj[u]:
            relaxations += 1
            nd = dist[u] + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                if not in_queue[v]:
                    queue.append(v)
                    in_queue[v] = True
                    enqueue_count[v] += 1
                    if enqueue_count[v] > V:
                        has_negative_cycle = True
                        queue.clear()
                        break
        if has_negative_cycle:
            break

    if counters is not None:
        counters["relaxations"] = counters.get("relaxations", 0) + relaxations

    return dist, prev, has_negative_cycle
