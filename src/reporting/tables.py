"""Generate summary CSV and Markdown/LaTeX tables from raw data."""

import pandas as pd
import numpy as np
from pathlib import Path


def summarise_sorting(raw_path: Path, out_path: Path) -> pd.DataFrame:
    """Read raw sorting CSV, compute summary stats, write summary CSV."""
    df = pd.read_csv(raw_path)
    df = df[df["skipped"].astype(str) != "True"]
    df["time_ns"] = pd.to_numeric(df["time_ns"], errors="coerce")
    df = df.dropna(subset=["time_ns"])

    summary = df.groupby(["algorithm", "size", "structure", "sort_key"]).agg(
        mean_ns=("time_ns", "mean"),
        std_ns=("time_ns", "std"),
        min_ns=("time_ns", "min"),
        median_ns=("time_ns", "median"),
        peak_mem_bytes=("peak_mem_bytes", "first"),
        rss_delta_bytes=("rss_delta_bytes", "first"),
        comparisons=("comparisons", "first"),
        swaps=("swaps", "first"),
    ).reset_index()

    # speedup vs timsort reference
    ref = summary[summary["algorithm"] == "timsort"][
        ["size", "structure", "sort_key", "mean_ns"]
    ].rename(columns={"mean_ns": "ref_ns"})
    summary = summary.merge(ref, on=["size", "structure", "sort_key"], how="left")
    summary["speedup_vs_timsort"] = summary["ref_ns"] / summary["mean_ns"].replace(0, np.nan)

    summary.to_csv(out_path, index=False)
    return summary


def summarise_graph(raw_path: Path, out_path: Path) -> pd.DataFrame:
    """Read raw graph CSV, compute summary stats, write summary CSV."""
    df = pd.read_csv(raw_path)
    df = df[df["skipped"].astype(str) != "True"]
    df["time_ns"] = pd.to_numeric(df["time_ns"], errors="coerce")
    df = df.dropna(subset=["time_ns"])

    summary = df.groupby(["algorithm", "graph_type", "V", "weight_mode"]).agg(
        mean_ns=("time_ns", "mean"),
        std_ns=("time_ns", "std"),
        min_ns=("time_ns", "min"),
        median_ns=("time_ns", "median"),
        peak_mem_bytes=("peak_mem_bytes", "first"),
        E=("E", "first"),
        relaxations=("relaxations", "first"),
    ).reset_index()

    summary.to_csv(out_path, index=False)
    return summary


def complexity_table() -> pd.DataFrame:
    """Return a DataFrame of theoretical complexities for all algorithms."""
    rows = [
        # sorting
        ("Insertion Sort", "O(n)", "O(n^2)", "O(n^2)", "O(1)", "Yes"),
        ("Merge Sort", "O(n log n)", "O(n log n)", "O(n log n)", "O(n)", "Yes"),
        ("Quick Sort (random pivot)", "O(n log n)", "O(n log n)", "O(n^2)*", "O(log n)", "No"),
        ("Quick Sort (naive pivot)", "O(n)", "O(n log n)", "O(n^2)", "O(log n)", "No"),
        ("Heap Sort", "O(n log n)", "O(n log n)", "O(n log n)", "O(1)", "No"),
        ("Radix Sort (LSD)", "O(d*n)", "O(d*n)", "O(d*n)", "O(n+k)", "Yes"),
        ("Timsort (reference)", "O(n)", "O(n log n)", "O(n log n)", "O(n)", "Yes"),
        # graph
        ("Dijkstra (heap)", "O((V+E) log V)", "O((V+E) log V)", "O((V+E) log V)", "O(V+E)", "N/A"),
        ("Dijkstra (array)", "O(V^2)", "O(V^2)", "O(V^2)", "O(V)", "N/A"),
        ("Bellman-Ford", "O(E)", "O(V*E)", "O(V*E)", "O(V+E)", "N/A"),
        ("SPFA", "O(E) avg", "O(k*E)", "O(V*E)", "O(V+E)", "N/A"),
    ]
    return pd.DataFrame(rows, columns=[
        "Algorithm", "Best Time", "Average Time", "Worst Time", "Space", "Stable"
    ])


def write_markdown_table(df: pd.DataFrame, path: Path, title: str = "") -> None:
    """Write a DataFrame to a Markdown table file without external dependencies."""
    with open(path, "w", encoding="utf-8") as f:
        if title:
            f.write(f"# {title}\n\n")
        headers = [str(c) for c in df.columns]
        f.write("| " + " | ".join(headers) + " |\n")
        f.write("| " + " | ".join(["---"] * len(headers)) + " |\n")
        for _, row in df.iterrows():
            f.write("| " + " | ".join(str(v) if pd.notna(v) else "" for v in row.values) + " |\n")
        f.write("\n")


def write_latex_table(df: pd.DataFrame, path: Path, caption: str = "", label: str = "") -> None:
    """Write a DataFrame to a LaTeX tabular environment."""
    n_cols = len(df.columns)
    col_fmt = "l" + "r" * (n_cols - 1)
    with open(path, "w") as f:
        f.write("\\begin{table}[htbp]\n\\centering\n")
        if caption:
            f.write(f"\\caption{{{caption}}}\n")
        if label:
            f.write(f"\\label{{{label}}}\n")
        f.write(f"\\begin{{tabular}}{{{col_fmt}}}\n\\hline\n")
        f.write(" & ".join(str(c) for c in df.columns) + " \\\\\n\\hline\n")
        for _, row in df.iterrows():
            f.write(" & ".join(str(v) for v in row.values) + " \\\\\n")
        f.write("\\hline\n\\end{tabular}\n\\end{table}\n")


def write_dijkstra_failures(raw_graph_path: Path, out_path: Path) -> None:
    """Extract and save rows where Dijkstra ran on negative-weight graphs."""
    df = pd.read_csv(raw_graph_path)
    dijkstra_neg = df[
        (df["algorithm"].isin(["dijkstra_heap", "dijkstra_array"]))
        & (df["weight_mode"].isin(["negative_safe", "negative_cycle"]))
        & (df["skipped"].astype(str) != "True")
    ]
    dijkstra_neg.to_csv(out_path, index=False)
