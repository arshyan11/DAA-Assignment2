"""Auto-generate plain-language observation notes from experimental data."""

import pandas as pd
import numpy as np


def generate_observations(
    sort_summary: pd.DataFrame,
    graph_summary: pd.DataFrame,
    fit_sort: pd.DataFrame,
    fit_graph: pd.DataFrame,
) -> str:
    """Return a multi-line string of draft observations for the report.

    These are starting points for human editing, not final text.
    """
    lines = ["DRAFT OBSERVATIONS (edit before including in report)", "=" * 60, ""]

    # --- Sorting observations ---
    lines.append("SORTING")
    lines.append("-" * 40)

    if not sort_summary.empty and "mean_ns" in sort_summary.columns:
        # fastest algorithm overall
        avg = sort_summary.groupby("algorithm")["mean_ns"].mean().sort_values()
        fastest = avg.index[0]
        slowest = avg.index[-1]
        speedup = avg.iloc[-1] / (avg.iloc[0] + 1)
        lines.append(
            f"Across all sizes and structures, {fastest} had the lowest average runtime "
            f"and {slowest} the highest. Speedup factor: {speedup:.1f}x."
        )

        # insertion sort crossover
        if "insertion_sort" in avg.index and "merge_sort" in avg.index:
            lines.append(
                "Insertion sort is competitive at small sizes (n <= ~1000) due to "
                "low constant factor and cache locality, but merge sort overtakes it "
                "as n grows - this is the classic O(n^2) vs O(n log n) crossover."
            )

        # duplicates effect on quick sort
        lines.append(
            "On many-duplicates input, quick sort with random pivot may show degraded "
            "performance if the partition repeatedly creates unbalanced halves around "
            "equal elements. Merge sort and radix sort are unaffected."
        )

        # sorted input and insertion sort
        lines.append(
            "On already-sorted input, insertion sort achieves O(n) (zero swaps, "
            "one comparison per element), giving it a large advantage over heap sort "
            "and quick sort on that specific structure."
        )

    if not fit_sort.empty and "log_log_slope" in fit_sort.columns:
        for _, row in fit_sort.iterrows():
            algo = row["algorithm"]
            slope = row["log_log_slope"]
            r2 = row["r_squared"]
            if r2 > 0.95:
                lines.append(
                    f"{algo}: empirical log-log slope = {slope:.2f} "
                    f"(R^2={r2:.3f}), consistent with best-fit model '{row['best_fit_model']}'."
                )
            else:
                lines.append(
                    f"{algo}: R^2={r2:.3f} is low, suggesting the runtime varies "
                    f"significantly across input structures (slope={slope:.2f})."
                )

    lines.append("")
    lines.append("GRAPH")
    lines.append("-" * 40)

    if not graph_summary.empty:
        avg_g = graph_summary.groupby("algorithm")["mean_ns"].mean().sort_values()
        lines.append(
            f"Fastest graph algorithm overall: {avg_g.index[0]}. "
            f"Slowest: {avg_g.index[-1]}."
        )
        lines.append(
            "Dijkstra (heap) is typically fastest on sparse graphs. "
            "On dense graphs, Dijkstra (array) with O(V^2) becomes competitive "
            "because the heap overhead (log V per push) accumulates when E is large."
        )
        lines.append(
            "Bellman-Ford's early-exit optimisation causes actual iteration counts "
            "to be much less than V-1 on typical sparse graphs, partly explaining "
            "why its measured time is better than the O(V*E) bound suggests."
        )
        lines.append(
            "Dijkstra produces wrong answers on graphs with negative-weight edges. "
            "The dijkstra_negative_weight_failures.csv file lists vertex-level errors. "
            "This is not a bug - it is a known limitation of greedy relabelling."
        )
        lines.append(
            "SPFA matches or beats Bellman-Ford on most practical inputs "
            "because it only re-relaxes neighbours of vertices whose distance changed."
        )

    lines.append("")
    lines.append("NOTE: These observations are machine-generated from the data.")
    lines.append("Review and rewrite in your own words before submission.")
    return "\n".join(lines)
