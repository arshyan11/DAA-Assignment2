"""Pytest suite for sorting algorithms."""

import copy
import random
import pytest

from algo_eval.src.sorting import SORT_REGISTRY
from algo_eval.src.generators.orders import generate_orders, deadline_key, priority_key, composite_key, zone_key


def _make_simple(n, seed=0):
    rng = random.Random(seed)
    return [rng.randint(0, 1000) for _ in range(n)]


def _test_sort(fn, key=lambda x: x, is_integer=False):
    """Helper: runs the sort function through several small cases."""
    cases = [
        [],
        [42],
        [3, 1, 4, 1, 5, 9, 2, 6],
        [1, 1, 1, 1],
        list(range(20, 0, -1)),
        list(range(20)),
    ]
    for case in cases:
        data = copy.deepcopy(case)
        if is_integer:
            fn(data, key=key)
            assert data == sorted(case, key=key), f"Failed on {case}"
        else:
            fn(data, key=key)
            assert [key(x) for x in data] == sorted(key(x) for x in case), f"Failed on {case}"


class TestInsertionSort:
    def test_basic(self):
        from algo_eval.src.sorting.insertion_sort import insertion_sort
        _test_sort(insertion_sort)

    def test_orders_deadline(self):
        from algo_eval.src.sorting.insertion_sort import insertion_sort
        orders = generate_orders(200, seed=1, structure="random")
        result = copy.deepcopy(orders)
        insertion_sort(result, key=deadline_key)
        ref = sorted(orders, key=deadline_key)
        assert [o.deadline for o in result] == [o.deadline for o in ref]

    def test_counters(self):
        from algo_eval.src.sorting.insertion_sort import insertion_sort
        data = [5, 3, 1, 4, 2]
        ctrs = {}
        insertion_sort(data, counters=ctrs)
        assert ctrs["comparisons"] > 0
        assert ctrs["swaps"] > 0

    def test_already_sorted_fast(self):
        from algo_eval.src.sorting.insertion_sort import insertion_sort
        data = list(range(100))
        ctrs = {}
        insertion_sort(data, counters=ctrs)
        assert ctrs["swaps"] == 0  # no swaps on sorted input


class TestMergeSort:
    def test_basic(self):
        from algo_eval.src.sorting.merge_sort import merge_sort
        _test_sort(merge_sort)

    def test_stability(self):
        from algo_eval.src.sorting.merge_sort import merge_sort
        orders = generate_orders(500, seed=2, structure="random")
        result = copy.deepcopy(orders)
        merge_sort(result, key=composite_key)
        ref = sorted(orders, key=composite_key)
        assert [o.order_id for o in result] == [o.order_id for o in ref], "Merge sort must be stable"

    def test_duplicates(self):
        from algo_eval.src.sorting.merge_sort import merge_sort
        data = [3, 3, 3, 1, 1, 2]
        merge_sort(data)
        assert data == [1, 1, 2, 3, 3, 3]

    def test_large_random(self):
        from algo_eval.src.sorting.merge_sort import merge_sort
        data = _make_simple(5000, seed=10)
        orig = copy.deepcopy(data)
        merge_sort(data)
        assert data == sorted(orig)


class TestQuickSort:
    def test_basic(self):
        from algo_eval.src.sorting.quick_sort import quick_sort
        _test_sort(quick_sort)

    def test_sorted_input_no_stack_overflow(self):
        from algo_eval.src.sorting.quick_sort import quick_sort
        data = list(range(10_000))
        quick_sort(data)
        assert data == list(range(10_000))

    def test_reverse_sorted(self):
        from algo_eval.src.sorting.quick_sort import quick_sort
        data = list(range(500, 0, -1))
        orig = copy.deepcopy(data)
        quick_sort(data)
        assert data == sorted(orig)

    def test_naive_worst_case_counts(self):
        """Naive pivot on sorted input should produce near-quadratic comparisons."""
        from algo_eval.src.sorting.quick_sort import quick_sort_naive
        data = list(range(500))
        ctrs = {}
        quick_sort_naive(data, counters=ctrs)
        n = 500
        # on sorted input naive pivot: comparisons approx n*(n-1)/2
        assert ctrs["comparisons"] > n * n // 4


class TestHeapSort:
    def test_basic(self):
        from algo_eval.src.sorting.heap_sort import heap_sort
        _test_sort(heap_sort)

    def test_large(self):
        from algo_eval.src.sorting.heap_sort import heap_sort
        data = _make_simple(3000, seed=7)
        orig = copy.deepcopy(data)
        heap_sort(data)
        assert data == sorted(orig)

    def test_negative_values(self):
        from algo_eval.src.sorting.heap_sort import heap_sort
        data = [-5, -1, -100, 0, 7, 3]
        heap_sort(data)
        assert data == sorted([-5, -1, -100, 0, 7, 3])


class TestRadixSort:
    def test_basic(self):
        from algo_eval.src.sorting.radix_sort import radix_sort
        data = [170, 45, 75, 90, 802, 24, 2, 66]
        radix_sort(data, key=lambda x: x)
        assert data == sorted([170, 45, 75, 90, 802, 24, 2, 66])

    def test_zone_id(self):
        from algo_eval.src.sorting.radix_sort import radix_sort
        orders = generate_orders(300, seed=5, structure="random")
        result = copy.deepcopy(orders)
        radix_sort(result, key=zone_key)
        ref = sorted(orders, key=zone_key)
        assert [o.zone_id for o in result] == [o.zone_id for o in ref]

    def test_stability_zone(self):
        from algo_eval.src.sorting.radix_sort import radix_sort
        orders = generate_orders(200, seed=6)
        result = copy.deepcopy(orders)
        radix_sort(result, key=zone_key)
        ref = sorted(orders, key=zone_key)
        assert [o.order_id for o in result] == [o.order_id for o in ref], "Radix sort must be stable"

    def test_all_same(self):
        from algo_eval.src.sorting.radix_sort import radix_sort
        data = [5] * 100
        radix_sort(data)
        assert data == [5] * 100


class TestGeneratorDeterminism:
    def test_same_seed_same_output(self):
        a = generate_orders(100, seed=42)
        b = generate_orders(100, seed=42)
        assert [o.order_id for o in a] == [o.order_id for o in b]
        assert [o.deadline for o in a] == [o.deadline for o in b]

    def test_different_seeds_different_output(self):
        a = generate_orders(100, seed=1)
        b = generate_orders(100, seed=2)
        assert [o.deadline for o in a] != [o.deadline for o in b]
