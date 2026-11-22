"""Radix sort (LSD, base-256) for integer keys - O(d*n) where d = number of bytes."""

from typing import Callable, Any


def radix_sort(
    data: list,
    key: Callable[[Any], int] = lambda x: x,
    counters: dict | None = None,
) -> list:
    """Sort data in-place by integer key using LSD radix sort (base 256).

    The key function must return a non-negative integer.
    """
    n = len(data)
    if n < 2:
        return data

    keys = [key(item) for item in data]
    max_val = max(keys) if keys else 0

    comparisons = 0
    swaps = 0

    shift = 0
    while (max_val >> shift) > 0:
        count = [0] * 256
        for k in keys:
            digit = (k >> shift) & 0xFF
            count[digit] += 1
            comparisons += 1

        # prefix sums
        for i in range(1, 256):
            count[i] += count[i - 1]

        # build output in reverse to keep stability
        output_data = [None] * n
        output_keys = [0] * n
        for i in range(n - 1, -1, -1):
            digit = (keys[i] >> shift) & 0xFF
            count[digit] -= 1
            pos = count[digit]
            output_data[pos] = data[i]
            output_keys[pos] = keys[i]
            swaps += 1

        # copy back
        for i in range(n):
            data[i] = output_data[i]
            keys[i] = output_keys[i]

        shift += 8

    if counters is not None:
        counters["comparisons"] = counters.get("comparisons", 0) + comparisons
        counters["swaps"] = counters.get("swaps", 0) + swaps
    return data
