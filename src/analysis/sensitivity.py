"""Sensitivity analysis: perturb weights and measure ranking stability."""

import numpy as np
import pandas as pd
from typing import Callable


def _apply_weights(df: pd.DataFrame, weights: dict[str, float], score_fn: Callable) -> list[str]:
    """Return ranked algorithm names given a weight dict."""
    scored = score_fn(df, weights)
    return scored.sort_values("weighted_total", ascending=False)["algorithm"].tolist()


def run_sensitivity(
    summary_df: pd.DataFrame,
    base_weights: dict[str, float],
    score_fn: Callable,
    n_trials: int = 1000,
    rng_seed: int = 99,
) -> pd.DataFrame:
    """Perturb weights using Dirichlet samples and count how often each algorithm ranks first.

    score_fn(df, weights) must return a DataFrame with columns algorithm, weighted_total.
    Returns a DataFrame with columns: algorithm, times_ranked_first, fraction.
    """
    rng = np.random.default_rng(rng_seed)
    keys = list(base_weights.keys())
    n_criteria = len(keys)
    counts: dict[str, int] = {}

    for _ in range(n_trials):
        raw = rng.dirichlet(np.ones(n_criteria))
        perturbed = {k: float(v) * 100 for k, v in zip(keys, raw)}
        try:
            ranked = _apply_weights(summary_df, perturbed, score_fn)
            winner = ranked[0] if ranked else "none"
        except Exception:
            winner = "none"
        counts[winner] = counts.get(winner, 0) + 1

    rows = [
        {"algorithm": algo, "times_ranked_first": cnt, "fraction": cnt / n_trials}
        for algo, cnt in sorted(counts.items(), key=lambda x: -x[1])
    ]
    return pd.DataFrame(rows)


def fixed_perturbation_analysis(
    summary_df: pd.DataFrame,
    base_weights: dict[str, float],
    score_fn: Callable,
    delta: float = 10.0,
) -> pd.DataFrame:
    """Shift each weight by +/-delta, renormalise, and report the top-ranked algorithm."""
    keys = list(base_weights.keys())
    rows = []
    for key in keys:
        for sign, label in [(+delta, f"+{delta}"), (-delta, f"-{delta}")]:
            perturbed = dict(base_weights)
            perturbed[key] = max(0, perturbed[key] + sign)
            total = sum(perturbed.values())
            perturbed = {k: v / total * 100 for k, v in perturbed.items()}
            try:
                ranked = _apply_weights(summary_df, perturbed, score_fn)
                winner = ranked[0] if ranked else "none"
            except Exception:
                winner = "none"
            rows.append({"perturbed_criterion": key, "perturbation": label, "top_ranked": winner})

    return pd.DataFrame(rows)
