"""Registry of all sorting algorithms available to the benchmark runner."""

from .insertion_sort import insertion_sort
from .merge_sort import merge_sort
from .quick_sort import quick_sort, quick_sort_naive
from .heap_sort import heap_sort
from .radix_sort import radix_sort


def timsort_reference(
    data: list,
    key=lambda x: x,
    counters: dict | None = None,
) -> list:
    """Python built-in sorted() used as an external reference baseline (not implemented here)."""
    result = sorted(data, key=key)
    data[:] = result
    return data


# name -> (function, requires_integer_key, is_stable, quadratic_cap)
SORT_REGISTRY: dict[str, dict] = {
    "insertion_sort": {
        "fn": insertion_sort,
        "stable": True,
        "integer_key_only": False,
        "quadratic_cap": 10_000,
        "label": "Insertion Sort",
    },
    "merge_sort": {
        "fn": merge_sort,
        "stable": True,
        "integer_key_only": False,
        "quadratic_cap": None,
        "label": "Merge Sort",
    },
    "quick_sort": {
        "fn": quick_sort,
        "stable": False,
        "integer_key_only": False,
        "quadratic_cap": None,
        "label": "Quick Sort (random pivot)",
    },
    "quick_sort_naive": {
        "fn": quick_sort_naive,
        "stable": False,
        "integer_key_only": False,
        "quadratic_cap": 10_000,
        "label": "Quick Sort (naive pivot)",
    },
    "heap_sort": {
        "fn": heap_sort,
        "stable": False,
        "integer_key_only": False,
        "quadratic_cap": None,
        "label": "Heap Sort",
    },
    "radix_sort": {
        "fn": radix_sort,
        "stable": True,
        "integer_key_only": True,
        "quadratic_cap": None,
        "label": "Radix Sort (LSD base-256)",
    },
    "timsort": {
        "fn": timsort_reference,
        "stable": True,
        "integer_key_only": False,
        "quadratic_cap": None,
        "label": "Timsort (built-in reference)",
    },
}
