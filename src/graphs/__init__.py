"""Registry of graph algorithms."""

from .dijkstra_heap import dijkstra_heap
from .dijkstra_array import dijkstra_array
from .bellman_ford import bellman_ford
from .spfa import spfa
from .graph import Graph

GRAPH_REGISTRY: dict[str, dict] = {
    "dijkstra_heap": {
        "fn": dijkstra_heap,
        "handles_negative": False,
        "detects_negative_cycle": False,
        "label": "Dijkstra (binary heap)",
        "dense_cap": 1000,
    },
    "dijkstra_array": {
        "fn": dijkstra_array,
        "handles_negative": False,
        "detects_negative_cycle": False,
        "label": "Dijkstra (plain array)",
        "dense_cap": 1000,
    },
    "bellman_ford": {
        "fn": bellman_ford,
        "handles_negative": True,
        "detects_negative_cycle": True,
        "label": "Bellman-Ford",
        "dense_cap": 1000,
    },
    "spfa": {
        "fn": spfa,
        "handles_negative": True,
        "detects_negative_cycle": True,
        "label": "SPFA (bonus)",
        "dense_cap": 1000,
    },
}
