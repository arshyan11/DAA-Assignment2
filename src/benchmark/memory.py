"""Memory measurement utilities using tracemalloc and psutil."""

import tracemalloc
import psutil
import os
from typing import Callable


def measure_peak_memory(fn: Callable, *args, **kwargs) -> dict:
    """Run fn(*args, **kwargs) in a separate tracemalloc session.

    Returns peak_bytes (tracemalloc peak allocation) and rss_bytes
    (process RSS delta before/after).  Never called inside a timed run.
    """
    process = psutil.Process(os.getpid())
    rss_before = process.memory_info().rss

    tracemalloc.start()
    fn(*args, **kwargs)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    rss_after = process.memory_info().rss
    return {
        "peak_bytes": peak,
        "rss_delta_bytes": max(0, rss_after - rss_before),
    }
