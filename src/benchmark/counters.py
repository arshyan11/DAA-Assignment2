"""Operation counters: wrappers that count comparisons, swaps, relaxations."""


def fresh_counters() -> dict:
    """Return a new zeroed counter dict."""
    return {
        "comparisons": 0,
        "swaps": 0,
        "relaxations": 0,
        "heap_pushes": 0,
        "heap_pops": 0,
        "iterations": 0,
    }
