"""Insertion sort - stable, in-place, O(n^2) average and worst case."""

from typing import Callable, Any


def insertion_sort(
    data: list,
    key: Callable[[Any], Any] = lambda x: x,
    counters: dict | None = None,
) -> list:
    """Sort data in-place using insertion sort; return the same list."""
    arr = data
    cmps = 0
    swaps = 0
    n = len(arr)
    for i in range(1, n):
        current = arr[i]
        current_key = key(current)
        j = i - 1
        while j >= 0:
            cmps += 1
            if key(arr[j]) > current_key:
                arr[j + 1] = arr[j]
                swaps += 1
                j -= 1
            else:
                break
        arr[j + 1] = current
    if counters is not None:
        counters["comparisons"] = counters.get("comparisons", 0) + cmps
        counters["swaps"] = counters.get("swaps", 0) + swaps
    return arr
