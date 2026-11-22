"""Generate all benchmark figures as PNG (300 dpi) and SVG."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from pathlib import Path

# Consistent colour palette across all figures
ALGO_COLOURS = {
    "insertion_sort": "#e41a1c",
    "merge_sort": "#377eb8",
    "quick_sort": "#4daf4a",
    "quick_sort_naive": "#984ea3",
    "heap_sort": "#ff7f00",
    "radix_sort": "#a65628",
    "timsort": "#999999",
    "dijkstra_heap": "#1b9e77",
    "dijkstra_array": "#d95f02",
    "bellman_ford": "#7570b3",
    "spfa": "#e7298a",
}

ALGO_LABELS = {
    "insertion_sort": "Insertion Sort",
    "merge_sort": "Merge Sort",
    "quick_sort": "Quick Sort (rand. pivot)",
    "quick_sort_naive": "Quick Sort (naive pivot)",
    "heap_sort": "Heap Sort",
    "radix_sort": "Radix Sort",
    "timsort": "Timsort (reference)",
    "dijkstra_heap": "Dijkstra (heap)",
    "dijkstra_array": "Dijkstra (array)",
    "bellman_ford": "Bellman-Ford",
    "spfa": "SPFA",
}


def _save(fig: plt.Figure, path: Path, name: str) -> None:
    """Save figure as both PNG and SVG."""
    fig.savefig(path / f"{name}.png", dpi=300, bbox_inches="tight")
    fig.savefig(path / f"{name}.svg", bbox_inches="tight")
    plt.close(fig)


def plot_runtime_loglog(summary_df: pd.DataFrame, figures_dir: Path, task: str = "sorting") -> None:
    """Log-log runtime vs size for each input structure."""
    if "structure" in summary_df.columns:
        structures = summary_df["structure"].unique()
    else:
        structures = ["all"]
    size_col = "size" if "size" in summary_df.columns else "V"

    for struct in structures:
        if "structure" in summary_df.columns:
            sub = summary_df[summary_df["structure"] == struct]
        else:
            sub = summary_df

        fig, ax = plt.subplots(figsize=(9, 6))
        for algo, grp in sub.groupby("algorithm"):
            grp = grp.sort_values(size_col)
            colour = ALGO_COLOURS.get(algo, "#333333")
            label = ALGO_LABELS.get(algo, algo)
            ax.plot(
                grp[size_col], grp["mean_ns"] / 1e6,
                marker="o", linewidth=1.8, markersize=5,
                color=colour, label=label,
            )
            if "std_ns" in grp.columns:
                ax.fill_between(
                    grp[size_col],
                    (grp["mean_ns"] - grp["std_ns"]) / 1e6,
                    (grp["mean_ns"] + grp["std_ns"]) / 1e6,
                    alpha=0.15, color=colour,
                )

        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("Input size n", fontsize=12)
        ax.set_ylabel("Mean runtime (ms)", fontsize=12)
        struct_label = struct.replace("_", " ").title()
        ax.set_title(f"Runtime vs Size - {struct_label} ({task.title()})", fontsize=13)
        ax.legend(fontsize=9, loc="upper left")
        ax.grid(True, which="both", linestyle="--", alpha=0.4)
        _save(fig, figures_dir, f"runtime_loglog_{task}_{struct}")


def plot_memory(summary_df: pd.DataFrame, figures_dir: Path, task: str = "sorting") -> None:
    """Memory (peak_mem_bytes) vs size for all algorithms."""
    size_col = "size" if "size" in summary_df.columns else "V"
    fig, ax = plt.subplots(figsize=(9, 6))
    for algo, grp in summary_df.groupby("algorithm"):
        grp = grp.sort_values(size_col)
        colour = ALGO_COLOURS.get(algo, "#333333")
        label = ALGO_LABELS.get(algo, algo)
        ax.plot(
            grp[size_col], grp["peak_mem_bytes"] / 1024,
            marker="s", linewidth=1.8, markersize=5,
            color=colour, label=label,
        )
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Input size", fontsize=12)
    ax.set_ylabel("Peak memory (KB)", fontsize=12)
    ax.set_title(f"Memory Usage vs Size ({task.title()})", fontsize=13)
    ax.legend(fontsize=9)
    ax.grid(True, which="both", linestyle="--", alpha=0.4)
    _save(fig, figures_dir, f"memory_{task}")


def plot_weighted_scores(scores_df: pd.DataFrame, figures_dir: Path, task: str = "sorting") -> None:
    """Horizontal bar chart of total weighted scores."""
    df = scores_df.sort_values("weighted_total")
    fig, ax = plt.subplots(figsize=(9, max(4, len(df) * 0.7)))
    colours = [ALGO_COLOURS.get(a, "#555555") for a in df["algorithm"]]
    labels = [ALGO_LABELS.get(a, a) for a in df["algorithm"]]
    ax.barh(labels, df["weighted_total"], color=colours, edgecolor="white")
    ax.set_xlabel("Weighted Score (out of 100)", fontsize=12)
    ax.set_title(f"Algorithm Ranking - Weighted Scores ({task.title()})", fontsize=13)
    ax.set_xlim(0, 105)
    for i, v in enumerate(df["weighted_total"]):
        ax.text(v + 0.5, i, f"{v:.1f}", va="center", fontsize=9)
    _save(fig, figures_dir, f"weighted_scores_{task}")


def plot_time_theory_ratio(
    summary_df: pd.DataFrame,
    figures_dir: Path,
    task: str = "sorting",
) -> None:
    """Plot measured time / theoretical growth to show how well theory predicts practice."""
    size_col = "size" if "size" in summary_df.columns else "V"
    fig, ax = plt.subplots(figsize=(9, 6))

    for algo, grp in summary_df.groupby("algorithm"):
        grp = grp.sort_values(size_col)
        n = grp[size_col].values.astype(float)
        t = grp["mean_ns"].values.astype(float)

        # choose growth function based on task
        if task == "sorting":
            growth = n * np.log2(np.maximum(n, 2))
        else:
            growth = n * np.log2(np.maximum(n, 2))

        ratio = t / (growth + 1e-10)
        ratio /= ratio.mean() + 1e-10  # normalise to mean = 1 for comparison

        colour = ALGO_COLOURS.get(algo, "#333333")
        label = ALGO_LABELS.get(algo, algo)
        ax.plot(n, ratio, marker="o", linewidth=1.8, markersize=5, color=colour, label=label)

    ax.axhline(y=1.0, color="black", linestyle="--", linewidth=0.8, alpha=0.5)
    ax.set_xscale("log")
    ax.set_xlabel("Input size", fontsize=12)
    ax.set_ylabel("T(n) / (n log n)  [normalised]", fontsize=12)
    ax.set_title(f"Time / Theoretical Growth ({task.title()})", fontsize=13)
    ax.legend(fontsize=9)
    ax.grid(True, which="both", linestyle="--", alpha=0.4)
    _save(fig, figures_dir, f"time_theory_ratio_{task}")


def plot_operation_counts(summary_df: pd.DataFrame, figures_dir: Path) -> None:
    """Plot comparison/swap counts vs size for sorting algorithms."""
    if "comparisons" not in summary_df.columns:
        return
    size_col = "size"
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for algo, grp in summary_df.groupby("algorithm"):
        grp = grp.sort_values(size_col)
        colour = ALGO_COLOURS.get(algo, "#333333")
        label = ALGO_LABELS.get(algo, algo)
        grp_num = grp[grp["comparisons"].apply(pd.to_numeric, errors="coerce").notna()]
        if grp_num.empty:
            continue
        axes[0].plot(grp_num[size_col], pd.to_numeric(grp_num["comparisons"]),
                     marker="o", color=colour, label=label, linewidth=1.8, markersize=4)
        axes[1].plot(grp_num[size_col], pd.to_numeric(grp_num["swaps"]),
                     marker="s", color=colour, label=label, linewidth=1.8, markersize=4)

    for ax, title, ylabel in zip(
        axes,
        ["Comparisons vs Size", "Swaps vs Size"],
        ["Comparisons", "Swaps"],
    ):
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("Input size n", fontsize=11)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.set_title(title, fontsize=12)
        ax.legend(fontsize=8)
        ax.grid(True, which="both", linestyle="--", alpha=0.4)

    fig.tight_layout()
    _save(fig, figures_dir, "operation_counts_sorting")


def plot_sparse_vs_dense(summary_df: pd.DataFrame, figures_dir: Path) -> None:
    """Compare sparse vs dense graph runtime side by side."""
    if "graph_type" not in summary_df.columns:
        return
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for ax, gtype in zip(axes, ["sparse", "dense"]):
        sub = summary_df[summary_df["graph_type"] == gtype]
        for algo, grp in sub.groupby("algorithm"):
            grp = grp.sort_values("V")
            colour = ALGO_COLOURS.get(algo, "#333333")
            label = ALGO_LABELS.get(algo, algo)
            ax.plot(grp["V"], grp["mean_ns"] / 1e6,
                    marker="o", color=colour, label=label, linewidth=1.8, markersize=5)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("Vertices V", fontsize=11)
        ax.set_ylabel("Mean runtime (ms)", fontsize=11)
        ax.set_title(f"{gtype.title()} Graph Runtime", fontsize=12)
        ax.legend(fontsize=9)
        ax.grid(True, which="both", linestyle="--", alpha=0.4)
    fig.tight_layout()
    _save(fig, figures_dir, "sparse_vs_dense_graph")


def plot_sensitivity_heatmap(sensitivity_df: pd.DataFrame, figures_dir: Path, task: str) -> None:
    """Heatmap showing how often each algorithm ranks first under weight perturbation."""
    if sensitivity_df.empty or "algorithm" not in sensitivity_df.columns:
        return
    fig, ax = plt.subplots(figsize=(8, max(3, len(sensitivity_df) * 0.6)))
    algos = [ALGO_LABELS.get(a, a) for a in sensitivity_df["algorithm"]]
    fracs = sensitivity_df["fraction"].values * 100

    bars = ax.barh(algos, fracs, color=[
        ALGO_COLOURS.get(a, "#555555") for a in sensitivity_df["algorithm"]
    ], edgecolor="white")
    ax.set_xlabel("% of trials ranked first", fontsize=12)
    ax.set_title(f"Sensitivity Analysis: Rank-1 Frequency ({task.title()})", fontsize=13)
    ax.set_xlim(0, 110)
    for bar, frac in zip(bars, fracs):
        ax.text(frac + 0.5, bar.get_y() + bar.get_height() / 2,
                f"{frac:.1f}%", va="center", fontsize=9)
    _save(fig, figures_dir, f"sensitivity_heatmap_{task}")


def plot_stability_demo(summary_df: pd.DataFrame, figures_dir: Path) -> None:
    """Bar chart showing which algorithms preserved stability on composite key."""
    if "stable" not in summary_df.columns:
        return
    stable_data = summary_df[summary_df["sort_key"] == "composite"].groupby("algorithm")["stable"].first()
    if stable_data.empty:
        return
    fig, ax = plt.subplots(figsize=(9, 5))
    labels = [ALGO_LABELS.get(a, a) for a in stable_data.index]
    vals = stable_data.apply(lambda x: 1 if str(x) == "True" else 0).values
    colours_bar = [
        ALGO_COLOURS.get(a, "#555555") for a in stable_data.index
    ]
    ax.bar(labels, vals, color=colours_bar, edgecolor="white")
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["Unstable", "Stable"])
    ax.set_title("Stability on Composite (priority, deadline) Sort Key", fontsize=13)
    ax.set_xlabel("Algorithm", fontsize=12)
    plt.xticks(rotation=25, ha="right")
    _save(fig, figures_dir, "stability_demo")


def plot_stacked_contributions(scores_df: pd.DataFrame, figures_dir: Path, task: str = "sorting") -> None:
    """Stacked bar chart of criterion contributions to total weighted score."""
    df = scores_df.sort_values("weighted_total", ascending=True).copy()
    if df.empty:
        return

    labels = [ALGO_LABELS.get(a, a) for a in df["algorithm"]]
    fig, ax = plt.subplots(figsize=(10, max(4.5, len(df) * 0.75)))

    if task == "sorting":
        from ..analysis.criteria import SORTING_WEIGHTS as W
        cols_weights = [
            ("runtime_score", W["measured_runtime"] / 10.0, "Measured Runtime (30%)", "#377eb8"),
            ("theory_score", W["theoretical_complexity"] / 10.0, "Theory Complexity (15%)", "#4daf4a"),
            ("memory_score", W["memory"] / 10.0, "Memory Usage (15%)", "#984ea3"),
            ("stability_score", W["stability"] / 10.0, "Stability (15%)", "#ff7f00"),
            ("robustness_score", W["input_robustness"] / 10.0, "Input Robustness (15%)", "#ffff33"),
            ("suitability_score", W["data_type_suitability"] / 10.0, "Data Suitability (10%)", "#a65628"),
        ]
    else:
        from ..analysis.criteria import GRAPH_WEIGHTS as W
        cols_weights = [
            ("runtime_score", W["measured_runtime"] / 10.0, "Measured Runtime (30%)", "#377eb8"),
            ("theory_score", W["theoretical_complexity"] / 10.0, "Theory Complexity (15%)", "#4daf4a"),
            ("memory_score", W["memory"] / 10.0, "Memory Usage (10%)", "#984ea3"),
            ("neg_weight_score", W["correctness_negative"] / 10.0, "Negative Correctness (20%)", "#e41a1c"),
            ("scalability_score", W["scalability_sparse_dense"] / 10.0, "Scalability (15%)", "#ff7f00"),
            ("simplicity_score", W["implementation_simplicity"] / 10.0, "Simplicity (10%)", "#999999"),
        ]

    left = np.zeros(len(df))
    for col, factor, name, colour in cols_weights:
        val = (df[col] * factor).values if col in df.columns else np.zeros(len(df))
        ax.barh(labels, val, left=left, label=name, color=colour, edgecolor="white", height=0.65)
        left += val

    ax.set_xlabel("Weighted Score Component (out of 100)", fontsize=11)
    ax.set_title(f"Stacked Criterion Contribution to Overall Score ({task.title()})", fontsize=12)
    ax.set_xlim(0, 105)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8.5)
    ax.grid(True, axis="x", linestyle="--", alpha=0.4)
    _save(fig, figures_dir, f"stacked_contributions_{task}")


def plot_crossover(summary_df: pd.DataFrame, figures_dir: Path) -> None:
    """Plot insertion sort vs merge sort to show the crossover point."""
    if "size" not in summary_df.columns:
        return
    sub = summary_df[
        summary_df["algorithm"].isin(["insertion_sort", "merge_sort"])
        & (summary_df.get("structure", pd.Series(["random"] * len(summary_df))) == "random")
    ]
    if sub.empty:
        return
    fig, ax = plt.subplots(figsize=(9, 6))
    for algo, grp in sub.groupby("algorithm"):
        grp = grp.sort_values("size")
        colour = ALGO_COLOURS.get(algo, "#333333")
        label = ALGO_LABELS.get(algo, algo)
        ax.plot(grp["size"], grp["mean_ns"] / 1e6, marker="o", color=colour, label=label, linewidth=2)
    ax.set_xlabel("Input size n", fontsize=12)
    ax.set_ylabel("Mean runtime (ms)", fontsize=12)
    ax.set_title("Crossover: Insertion Sort vs Merge Sort (random input)", fontsize=13)
    ax.legend(fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.4)
    _save(fig, figures_dir, "crossover_insertion_vs_merge")
