"""Scoring: normalise measured data and compute weighted totals."""

import pandas as pd
import numpy as np
from .criteria import (
    SORTING_WEIGHTS, GRAPH_WEIGHTS,
    STABILITY_SCORES, DATA_SUITABILITY_SCORES, THEORETICAL_COMPLEXITY_SORT,
    NEGATIVE_WEIGHT_CORRECTNESS, THEORETICAL_COMPLEXITY_GRAPH, IMPLEMENTATION_SIMPLICITY,
)


def _minmax_score(series: pd.Series, lower_is_better: bool = True) -> pd.Series:
    """Normalise series to 0-10; lower_is_better inverts so 10 = best."""
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series([10.0] * len(series), index=series.index)
    normalised = (series - mn) / (mx - mn)
    if lower_is_better:
        return (1 - normalised) * 10
    return normalised * 10


def score_sorting(summary_df: pd.DataFrame) -> pd.DataFrame:
    """Compute weighted scores for each sorting algorithm.

    summary_df must have columns: algorithm, mean_ns, peak_mem_bytes.
    Returns a DataFrame with one row per algorithm and weighted_total column.
    """
    df = summary_df.groupby("algorithm").agg(
        mean_ns=("mean_ns", "mean"),
        peak_mem_bytes=("peak_mem_bytes", "mean"),
    ).reset_index()

    df["runtime_score"] = _minmax_score(df["mean_ns"], lower_is_better=True)
    df["memory_score"] = _minmax_score(df["peak_mem_bytes"], lower_is_better=True)

    # robustness: use coefficient of variation of mean_ns across structures
    robustness_df = summary_df.groupby("algorithm")["mean_ns"].std().reset_index()
    robustness_df.columns = ["algorithm", "std_ns"]
    mean_ns_df = summary_df.groupby("algorithm")["mean_ns"].mean().reset_index()
    mean_ns_df.columns = ["algorithm", "mean_ns_overall"]
    rob = robustness_df.merge(mean_ns_df, on="algorithm")
    rob["cv"] = rob["std_ns"] / (rob["mean_ns_overall"] + 1)
    df = df.merge(rob[["algorithm", "cv"]], on="algorithm", how="left")
    df["robustness_score"] = _minmax_score(df["cv"].fillna(0), lower_is_better=True)

    df["stability_score"] = df["algorithm"].map(STABILITY_SCORES).fillna(0)
    df["theory_score"] = df["algorithm"].map(THEORETICAL_COMPLEXITY_SORT).fillna(0)
    df["suitability_score"] = df["algorithm"].map(DATA_SUITABILITY_SCORES).fillna(0)

    w = SORTING_WEIGHTS
    df["weighted_total"] = (
        df["runtime_score"] * w["measured_runtime"]
        + df["theory_score"] * w["theoretical_complexity"]
        + df["memory_score"] * w["memory"]
        + df["stability_score"] * w["stability"]
        + df["robustness_score"] * w["input_robustness"]
        + df["suitability_score"] * w["data_type_suitability"]
    ) / 10.0  # normalise to 100-point scale

    df = df.sort_values("weighted_total", ascending=False).reset_index(drop=True)
    df["rank"] = df["weighted_total"].rank(ascending=False, method="min").astype(int)
    return df


def score_graph(summary_df: pd.DataFrame) -> pd.DataFrame:
    """Compute weighted scores for each graph algorithm."""
    df = summary_df.groupby("algorithm").agg(
        mean_ns=("mean_ns", "mean"),
        peak_mem_bytes=("peak_mem_bytes", "mean"),
    ).reset_index()

    df["runtime_score"] = _minmax_score(df["mean_ns"], lower_is_better=True)
    df["memory_score"] = _minmax_score(df["peak_mem_bytes"], lower_is_better=True)

    # scalability: performance ratio sparse vs dense (lower ratio = better for all)
    if "graph_type" in summary_df.columns:
        sparse = summary_df[summary_df["graph_type"] == "sparse"].groupby("algorithm")["mean_ns"].mean()
        dense = summary_df[summary_df["graph_type"] == "dense"].groupby("algorithm")["mean_ns"].mean()
        ratio = (dense / (sparse + 1)).reset_index()
        ratio.columns = ["algorithm", "dense_sparse_ratio"]
        df = df.merge(ratio, on="algorithm", how="left")
        df["scalability_score"] = _minmax_score(
            df["dense_sparse_ratio"].fillna(df["dense_sparse_ratio"].max()), lower_is_better=True
        )
    else:
        df["scalability_score"] = 5.0

    df["neg_weight_score"] = df["algorithm"].map(NEGATIVE_WEIGHT_CORRECTNESS).fillna(0)
    df["theory_score"] = df["algorithm"].map(THEORETICAL_COMPLEXITY_GRAPH).fillna(0)
    df["simplicity_score"] = df["algorithm"].map(IMPLEMENTATION_SIMPLICITY).fillna(0)

    w = GRAPH_WEIGHTS
    df["weighted_total"] = (
        df["runtime_score"] * w["measured_runtime"]
        + df["theory_score"] * w["theoretical_complexity"]
        + df["memory_score"] * w["memory"]
        + df["neg_weight_score"] * w["correctness_negative"]
        + df["scalability_score"] * w["scalability_sparse_dense"]
        + df["simplicity_score"] * w["implementation_simplicity"]
    ) / 10.0

    df = df.sort_values("weighted_total", ascending=False).reset_index(drop=True)
    df["rank"] = df["weighted_total"].rank(ascending=False, method="min").astype(int)
    return df
