"""Heap sort - in-place, O(n log n), not stable."""

from typing import Callable, Any


def heap_sort(
    data: list,
    key: Callable[[Any], Any] = lambda x: x,
    counters: dict | None = None,
) -> list:
    """Sort data in-place using heap sort; return the same list."""
    n = len(data)
    cmps = 0
    swaps = 0

    def sift_down(arr, root, end):
        nonlocal cmps, swaps
        while True:
            largest = root
            left = 2 * root + 1
            right = 2 * root + 2
            if left < end:
                cmps += 1
                if key(arr[left]) > key(arr[largest]):
                    largest = left
            if right < end:
                cmps += 1
                if key(arr[right]) > key(arr[largest]):
                    largest = right
            if largest == root:
                break
            arr[root], arr[largest] = arr[largest], arr[root]
            swaps += 1
            root = largest

    # build max-heap
    for i in range(n // 2 - 1, -1, -1):
        sift_down(data, i, n)

    # extract elements
    for end in range(n - 1, 0, -1):
        data[0], data[end] = data[end], data[0]
        swaps += 1
        sift_down(data, 0, end)

    if counters is not None:
        counters["comparisons"] = counters.get("comparisons", 0) + cmps
        counters["swaps"] = counters.get("swaps", 0) + swaps
    return data
