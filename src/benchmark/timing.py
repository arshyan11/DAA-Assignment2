"""Timing utilities: perf_counter_ns timing with gc control and warm-up."""

import gc
import time
import statistics
from typing import Callable


def timed_run(
    fn: Callable,
    *args,
    repeats: int = 5,
    warmup: int = 1,
    **kwargs,
) -> dict:
    """Time fn(*args, **kwargs) for `repeats` runs after `warmup` warm-up runs.

    GC is disabled during each timed call and re-enabled immediately after.
    Returns a dict with keys: mean_ns, std_ns, min_ns, median_ns, times_ns.
    """
    for _ in range(warmup):
        fn(*args, **kwargs)

    times = []
    for _ in range(repeats):
        gc.disable()
        start = time.perf_counter_ns()
        fn(*args, **kwargs)
        elapsed = time.perf_counter_ns() - start
        gc.enable()
        times.append(elapsed)

    return {
        "mean_ns": statistics.mean(times),
        "std_ns": statistics.stdev(times) if len(times) > 1 else 0.0,
        "min_ns": min(times),
        "median_ns": statistics.median(times),
        "times_ns": times,
    }
