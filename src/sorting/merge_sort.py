"""Merge sort - top-down, stable, O(n log n), uses one reusable auxiliary buffer."""

from typing import Callable, Any


def merge_sort(
    data: list,
    key: Callable[[Any], Any] = lambda x: x,
    counters: dict | None = None,
) -> list:
    """Sort data in-place using top-down merge sort; return the same list."""
    n = len(data)
    if n < 2:
        return data
    aux = data[:]
    cmps = 0
    swaps = 0

    def merge(arr, buf, lo, mid, hi):
        nonlocal cmps, swaps
        buf[lo:hi] = arr[lo:hi]
        left = lo
        right = mid
        for k in range(lo, hi):
            if left >= mid:
                arr[k] = buf[right]
                right += 1
                swaps += 1
            elif right >= hi:
                arr[k] = buf[left]
                left += 1
                swaps += 1
            elif key(buf[right]) < key(buf[left]):
                cmps += 1
                arr[k] = buf[right]
                right += 1
                swaps += 1
            else:
                cmps += 1
                arr[k] = buf[left]
                left += 1
                swaps += 1

    def sort(arr, buf, lo, hi):
        if hi - lo < 2:
            return
        mid = (lo + hi) // 2
        sort(arr, buf, lo, mid)
        sort(arr, buf, mid, hi)
        merge(arr, buf, lo, mid, hi)

    import sys
    old_limit = sys.getrecursionlimit()
    needed = max(1000, 2 * (n.bit_length() + 1))
    sys.setrecursionlimit(max(old_limit, needed))
    sort(data, aux, 0, n)
    sys.setrecursionlimit(old_limit)

    if counters is not None:
        counters["comparisons"] = counters.get("comparisons", 0) + cmps
        counters["swaps"] = counters.get("swaps", 0) + swaps
    return data
