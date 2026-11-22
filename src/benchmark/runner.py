"""Main benchmark runner: orchestrates sorting and graph experiments."""

import csv
import copy
import logging
import os
from pathlib import Path
from typing import Callable

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs):
        return iterable

from .timing import timed_run
from .memory import measure_peak_memory
from .counters import fresh_counters

logger = logging.getLogger(__name__)


def _write_row(writer, row: dict) -> None:
    writer.writerow(row)


def run_sorting_experiments(
    algorithms: dict,
    sizes: list[int],
    structures: list[str],
    sort_keys: dict,
    generate_fn: Callable,
    output_path: Path,
    global_seed: int,
    repeats_small: int = 7,
    repeats_large: int = 3,
    large_threshold: int = 100_000,
    resume: bool = False,
) -> None:
    """Run all sorting experiments and append rows to output_path CSV."""
    fieldnames = [
        "algorithm", "size", "structure", "sort_key", "run_index",
        "time_ns", "peak_mem_bytes", "rss_delta_bytes",
        "comparisons", "swaps", "correctness", "stable", "seed", "skipped",
    ]
    already_done: set[tuple] = set()

    if resume and output_path.exists():
        with open(output_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                already_done.add((
                    row["algorithm"], row["size"], row["structure"],
                    row["sort_key"], row["run_index"],
                ))

    from ..generators.orders import STRUCTURE_KEY_MAP

    mode = "a" if (resume and output_path.exists()) else "w"
    with open(output_path, mode, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if mode == "w":
            writer.writeheader()

        cases = [(struct, k_name, k_fn) for struct in structures for k_name, k_fn in [STRUCTURE_KEY_MAP.get(struct, ("deadline", sort_keys.get("deadline")))]]
        total = len(algorithms) * len(sizes) * len(cases)
        pbar = tqdm(total=total, desc="Sorting experiments")

        for algo_name, algo_info in algorithms.items():
            fn = algo_info["fn"]
            cap = algo_info.get("quadratic_cap")
            is_integer_only = algo_info.get("integer_key_only", False)

            for size in sizes:
                is_capped = cap is not None and size > cap
                repeats = repeats_small if size <= large_threshold else repeats_large

                for structure, key_name, key_fn in cases:
                    pbar.update(1)

                    is_int_key = key_name in ("zone_id", "priority")
                    skipped = is_capped or (is_integer_only and not is_int_key)

                    dataset_seed = global_seed ^ (hash(f"{size}{structure}{key_name}") & 0xFFFFFF)

                    if skipped:
                        done_key = (algo_name, str(size), structure, key_name, "0")
                        if done_key in already_done:
                            continue
                        row = {
                            "algorithm": algo_name, "size": size,
                            "structure": structure, "sort_key": key_name,
                            "run_index": 0, "time_ns": "", "peak_mem_bytes": "",
                            "rss_delta_bytes": "", "comparisons": "", "swaps": "",
                            "correctness": "", "stable": "", "seed": dataset_seed,
                            "skipped": True,
                        }
                        _write_row(writer, row)
                        f.flush()
                        continue

                    done_key_check = (algo_name, str(size), structure, key_name, "0")
                    if done_key_check in already_done:
                        continue

                    raw_data = generate_fn(size, seed=dataset_seed, structure=structure)

                    check_data = copy.deepcopy(raw_data)
                    check_key = key_fn
                    fn(check_data, key=check_key)
                    ref = sorted(raw_data, key=check_key)
                    correct = all(
                        check_key(a) == check_key(b)
                        for a, b in zip(check_data, ref)
                    )
                    is_stable = algo_info.get("stable", False)
                    stability_ok = True
                    if is_stable and key_name == "composite":
                        for a, b in zip(check_data, ref):
                            if a.order_id != b.order_id:
                                stability_ok = False
                                break

                    # memory measurement (separate pass, not timed)
                    mem_data = copy.deepcopy(raw_data)
                    mem_info = measure_peak_memory(fn, mem_data, key=check_key)

                    # operation count pass
                    count_data = copy.deepcopy(raw_data)
                    ctrs = fresh_counters()
                    fn(count_data, key=check_key, counters=ctrs)

                    # timing passes
                    def _sort_copy():
                        d = copy.deepcopy(raw_data)
                        fn(d, key=check_key)

                    timing = timed_run(_sort_copy, repeats=repeats, warmup=1)

                    for run_i, t in enumerate(timing["times_ns"]):
                        done_key = (algo_name, str(size), structure, key_name, str(run_i))
                        if done_key in already_done:
                            continue
                        row = {
                            "algorithm": algo_name, "size": size,
                            "structure": structure, "sort_key": key_name,
                            "run_index": run_i, "time_ns": t,
                            "peak_mem_bytes": mem_info["peak_bytes"],
                            "rss_delta_bytes": mem_info["rss_delta_bytes"],
                            "comparisons": ctrs["comparisons"],
                            "swaps": ctrs["swaps"],
                            "correctness": correct,
                            "stable": stability_ok,
                            "seed": dataset_seed,
                            "skipped": False,
                        }
                        _write_row(writer, row)
                    f.flush()
                    logger.info("done: %s n=%d str=%s key=%s", algo_name, size, structure, key_name)

        pbar.close()


def run_graph_experiments(
    algorithms: dict,
    sparse_sizes: list[tuple[int, int]],
    dense_sizes: list[int],
    weight_modes: list[str],
    make_sparse_fn: Callable,
    make_dense_fn: Callable,
    output_path: Path,
    global_seed: int,
    repeats_small: int = 7,
    repeats_large: int = 3,
    large_threshold: int = 2000,
    resume: bool = False,
) -> None:
    """Run all graph SSSP experiments and append rows to output_path CSV."""
    fieldnames = [
        "algorithm", "graph_type", "V", "E", "weight_mode", "run_index",
        "time_ns", "peak_mem_bytes", "rss_delta_bytes",
        "relaxations", "heap_pushes", "heap_pops", "iterations",
        "correct", "negative_cycle_detected", "seed", "skipped",
    ]
    already_done: set[tuple] = set()

    if resume and output_path.exists():
        with open(output_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                already_done.add((
                    row["algorithm"], row["graph_type"], row["V"],
                    row["weight_mode"], row["run_index"],
                ))

    mode = "a" if (resume and output_path.exists()) else "w"
    with open(output_path, mode, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if mode == "w":
            writer.writeheader()

        configs = []
        for rows, cols in sparse_sizes:
            configs.append(("sparse", rows, cols, None))
        for V in dense_sizes:
            configs.append(("dense", None, None, V))

        pbar = tqdm(
            total=len(algorithms) * len(configs) * len(weight_modes),
            desc="Graph experiments",
        )

        from ..graphs.bellman_ford import bellman_ford as bf_ref

        for algo_name, algo_info in algorithms.items():
            fn = algo_info["fn"]
            handles_neg = algo_info["handles_negative"]
            detects_cycle = algo_info["detects_negative_cycle"]
            dense_cap = algo_info.get("dense_cap")

            for gtype, rows, cols, dense_V in configs:
                for wmode in weight_modes:
                    pbar.update(1)

                    if gtype == "sparse":
                        V = rows * cols
                    else:
                        V = dense_V

                    done_key_check = (algo_name, gtype, str(V), wmode, "0")
                    if done_key_check in already_done:
                        continue

                    is_dijkstra = algo_name in ("dijkstra_heap", "dijkstra_array")
                    if is_dijkstra and wmode == "negative_cycle":
                        row = {
                            "algorithm": algo_name, "graph_type": gtype,
                            "V": V, "E": "", "weight_mode": wmode,
                            "run_index": 0, "time_ns": "", "peak_mem_bytes": "",
                            "rss_delta_bytes": "", "relaxations": "",
                            "heap_pushes": "", "heap_pops": "", "iterations": "",
                            "correct": "", "negative_cycle_detected": "",
                            "seed": global_seed ^ (hash(f"{gtype}{V}{wmode}") & 0xFFFFFF),
                            "skipped": True,
                        }
                        _write_row(writer, row)
                        f.flush()
                        continue

                    if gtype == "sparse":
                        graph_seed = global_seed ^ (hash(f"sparse{rows}{cols}{wmode}") & 0xFFFFFF)
                        g = make_sparse_fn(rows, cols, seed=graph_seed, weight_mode=wmode)
                    else:
                        graph_seed = global_seed ^ (hash(f"dense{V}{wmode}") & 0xFFFFFF)
                        if dense_cap is not None and V > dense_cap:
                            row = {
                                "algorithm": algo_name, "graph_type": gtype,
                                "V": V, "E": "", "weight_mode": wmode,
                                "run_index": 0, "time_ns": "", "peak_mem_bytes": "",
                                "rss_delta_bytes": "", "relaxations": "",
                                "heap_pushes": "", "heap_pops": "", "iterations": "",
                                "correct": "", "negative_cycle_detected": "",
                                "seed": graph_seed, "skipped": True,
                            }
                            _write_row(writer, row)
                            f.flush()
                            continue
                        g = make_dense_fn(V, seed=graph_seed, weight_mode=wmode)

                    source = 0
                    E = g.num_edges()
                    repeats = repeats_small if V <= large_threshold else repeats_large

                    # reference answer (Bellman-Ford, handles all modes)
                    ref_dist, _, ref_cycle = bf_ref(g, source)
                    is_neg_cycle = wmode == "negative_cycle"

                    # skip Dijkstra on negative-weight graphs but still run and record failure
                    should_flag_wrong = not handles_neg and g.has_negative_weights()

                    # determine if algo returns a 3-tuple or 2-tuple
                    returns_cycle = detects_cycle

                    ctrs = fresh_counters()
                    if returns_cycle:
                        dist_check, _, cycle_detected = fn(g, source, counters=ctrs)
                    else:
                        dist_check, _ = fn(g, source, counters=ctrs)
                        cycle_detected = False

                    import math
                    tol = 1e-6
                    correct = all(
                        (math.isinf(a) and math.isinf(b)) or abs(a - b) < tol
                        for a, b in zip(dist_check, ref_dist)
                    ) if not is_neg_cycle else True

                    mem_info = measure_peak_memory(
                        fn, g, source
                    )

                    def _run():
                        if returns_cycle:
                            fn(g, source)
                        else:
                            fn(g, source)

                    timing = timed_run(_run, repeats=repeats, warmup=1)

                    for run_i, t in enumerate(timing["times_ns"]):
                        done_key = (algo_name, gtype, str(V), wmode, str(run_i))
                        if done_key in already_done:
                            continue
                        row = {
                            "algorithm": algo_name, "graph_type": gtype,
                            "V": V, "E": E, "weight_mode": wmode,
                            "run_index": run_i, "time_ns": t,
                            "peak_mem_bytes": mem_info["peak_bytes"],
                            "rss_delta_bytes": mem_info["rss_delta_bytes"],
                            "relaxations": ctrs["relaxations"],
                            "heap_pushes": ctrs["heap_pushes"],
                            "heap_pops": ctrs["heap_pops"],
                            "iterations": ctrs["iterations"],
                            "correct": correct,
                            "negative_cycle_detected": cycle_detected,
                            "seed": graph_seed,
                            "skipped": False,
                        }
                        _write_row(writer, row)
                    f.flush()
                    logger.info("done: %s %s V=%d wmode=%s", algo_name, gtype, V, wmode)

        pbar.close()
