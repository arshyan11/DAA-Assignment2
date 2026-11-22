"""Quick sort - iterative, random pivot (stack-safe); also naive first-pivot variant for worst-case demo."""

import random
from typing import Callable, Any


def _partition_random(arr, lo, hi, key, rng, cmps_ref, swaps_ref):
    pivot_idx = rng.randint(lo, hi)
    pivot_key = key(arr[pivot_idx])
    i = lo - 1
    j = hi + 1
    while True:
        while True:
            i += 1
            cmps_ref[0] += 1
            if key(arr[i]) >= pivot_key:
                break
        while True:
            j -= 1
            cmps_ref[0] += 1
            if key(arr[j]) <= pivot_key:
                break
        if i >= j:
            return j
        arr[i], arr[j] = arr[j], arr[i]
        swaps_ref[0] += 1


def quick_sort(
    data: list,
    key: Callable[[Any], Any] = lambda x: x,
    counters: dict | None = None,
    seed: int = 42,
) -> list:
    """Sort data in-place using iterative quick sort with random pivot (Hoare partition)."""
    n = len(data)
    if n < 2:
        return data
    rng = random.Random(seed)
    cmps_ref = [0]
    swaps_ref = [0]
    stack = [(0, n - 1)]
    while stack:
        lo, hi = stack.pop()
        if lo >= hi:
            continue
        p = _partition_random(data, lo, hi, key, rng, cmps_ref, swaps_ref)
        if (p - lo) > (hi - p - 1):
            stack.append((lo, p))
            stack.append((p + 1, hi))
        else:
            stack.append((p + 1, hi))
            stack.append((lo, p))
    if counters is not None:
        counters["comparisons"] = counters.get("comparisons", 0) + cmps_ref[0]
        counters["swaps"] = counters.get("swaps", 0) + swaps_ref[0]
    return data


def _partition_first(arr, lo, hi, key, cmps_ref, swaps_ref):
    pivot_key = key(arr[lo])
    arr[lo], arr[hi] = arr[hi], arr[lo]
    swaps_ref[0] += 1
    i = lo - 1
    for j in range(lo, hi):
        cmps_ref[0] += 1
        if key(arr[j]) <= pivot_key:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
            swaps_ref[0] += 1
    arr[i + 1], arr[hi] = arr[hi], arr[i + 1]
    swaps_ref[0] += 1
    return i + 1


def quick_sort_naive(
    data: list,
    key: Callable[[Any], Any] = lambda x: x,
    counters: dict | None = None,
) -> list:
    """First-pivot quick sort - demonstrates O(n^2) worst case on sorted input.

    Only intended for capped sizes where the quadratic behaviour is observable
    without timing out.
    """
    n = len(data)
    if n < 2:
        return data
    cmps_ref = [0]
    swaps_ref = [0]
    stack = [(0, n - 1)]
    while stack:
        lo, hi = stack.pop()
        if lo >= hi:
            continue
        p = _partition_first(data, lo, hi, key, cmps_ref, swaps_ref)
        stack.append((lo, p - 1))
        stack.append((p + 1, hi))
    if counters is not None:
        counters["comparisons"] = counters.get("comparisons", 0) + cmps_ref[0]
        counters["swaps"] = counters.get("swaps", 0) + swaps_ref[0]
    return data
