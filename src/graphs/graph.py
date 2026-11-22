"""Graph representation used by all shortest-path algorithms."""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Graph:
    """Adjacency-list weighted directed graph."""
    num_vertices: int
    adj: list[list[tuple[int, float]]] = field(default_factory=list)

    def __post_init__(self):
        if not self.adj:
            self.adj = [[] for _ in range(self.num_vertices)]

    def add_edge(self, u: int, v: int, weight: float) -> None:
        """Add a directed edge from u to v with the given weight."""
        self.adj[u].append((v, weight))

    def add_undirected_edge(self, u: int, v: int, weight: float) -> None:
        """Add an undirected (bidirectional) edge."""
        self.adj[u].append((v, weight))
        self.adj[v].append((u, weight))

    def num_edges(self) -> int:
        return sum(len(nbrs) for nbrs in self.adj)

    def has_negative_weights(self) -> bool:
        return any(w < 0 for nbrs in self.adj for _, w in nbrs)
