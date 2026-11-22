"""Evaluation criteria and weights for scoring algorithms."""

# Weights must sum to 100 for each task.

SORTING_WEIGHTS: dict[str, float] = {
    "measured_runtime": 30,
    "theoretical_complexity": 15,
    "memory": 15,
    "stability": 15,
    "input_robustness": 15,
    "data_type_suitability": 10,
}

GRAPH_WEIGHTS: dict[str, float] = {
    "measured_runtime": 30,
    "theoretical_complexity": 15,
    "memory": 10,
    "correctness_negative": 20,
    "scalability_sparse_dense": 15,
    "implementation_simplicity": 10,
}

assert abs(sum(SORTING_WEIGHTS.values()) - 100) < 1e-9, "Sorting weights must sum to 100"
assert abs(sum(GRAPH_WEIGHTS.values()) - 100) < 1e-9, "Graph weights must sum to 100"

# Fixed qualitative scores (0-10 scale) for criteria that cannot be measured automatically.

# Stability: 10 = stable, 0 = not stable
STABILITY_SCORES: dict[str, float] = {
    "insertion_sort": 10,
    "merge_sort": 10,
    "quick_sort": 0,
    "quick_sort_naive": 0,
    "heap_sort": 0,
    "radix_sort": 10,
    "timsort": 10,
}

# Suitability for the delivery-order data type (composite, mixed keys, real-world volume)
DATA_SUITABILITY_SCORES: dict[str, float] = {
    "insertion_sort": 3,   # good for small or nearly sorted, poor at scale
    "merge_sort": 8,       # general purpose, stable, O(n log n)
    "quick_sort": 7,       # fast in practice, not stable
    "quick_sort_naive": 2, # only for small sizes; O(n^2) on sorted input
    "heap_sort": 6,        # in-place, O(n log n), not stable
    "radix_sort": 7,       # linear for integer keys (priority/zone), not general
    "timsort": 10,         # Python's production sort, adaptive, stable
}

# Theoretical complexity scores (10 = best, 0 = worst among candidates)
THEORETICAL_COMPLEXITY_SORT: dict[str, float] = {
    "insertion_sort": 2,   # O(n^2) average/worst
    "merge_sort": 9,       # O(n log n) guaranteed
    "quick_sort": 8,       # O(n log n) average, O(n^2) worst (rare with random pivot)
    "quick_sort_naive": 2, # O(n^2) worst case on sorted input
    "heap_sort": 9,        # O(n log n) guaranteed
    "radix_sort": 10,      # O(d*n) - linear when d is small
    "timsort": 9,          # O(n log n) worst, O(n) on partially sorted
}

# Correctness on negative-weight graphs (0 = wrong, 10 = correct + detects cycle)
NEGATIVE_WEIGHT_CORRECTNESS: dict[str, float] = {
    "dijkstra_heap": 0,    # produces wrong answers on negative weights
    "dijkstra_array": 0,   # same
    "bellman_ford": 10,    # correct + detects negative cycles
    "spfa": 8,             # correct + heuristic cycle detection
}

# Theoretical complexity scores for graph algorithms
THEORETICAL_COMPLEXITY_GRAPH: dict[str, float] = {
    "dijkstra_heap": 9,    # O((V+E) log V)
    "dijkstra_array": 5,   # O(V^2)
    "bellman_ford": 4,     # O(V*E)
    "spfa": 7,             # O(k*E) average, O(V*E) worst
}

# Implementation simplicity (0-10; subjective but consistent)
IMPLEMENTATION_SIMPLICITY: dict[str, float] = {
    "dijkstra_heap": 7,
    "dijkstra_array": 8,
    "bellman_ford": 9,
    "spfa": 6,
}
