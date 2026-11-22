"""Curve fitting: fit runtime vs size to theoretical growth functions."""

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit  # type: ignore


def _safe_log(x):
    return np.log(np.maximum(x, 1e-10))


def _growth_nlogn(n, c):
    return c * n * np.log2(np.maximum(n, 2))


def _growth_n2(n, c):
    return c * n ** 2


def _growth_n(n, c):
    return c * n


def _growth_vlogv_e(ve, c):
    # combined (V log V + E)
    return c * ve


def _growth_v2(v, c):
    return c * v ** 2


def _growth_ve(ve, c):
    return c * ve


def fit_sorting(df: pd.DataFrame) -> pd.DataFrame:
    """Fit timing data for sorting algorithms.

    df must have columns: algorithm, size, mean_ns.
    Returns a DataFrame with one row per (algorithm, structure) with fit results.
    """
    results = []
    group_cols = ["algorithm"] + (["structure"] if "structure" in df.columns else [])

    for keys, grp in df.groupby(group_cols):
        if isinstance(keys, str):
            keys = (keys,)
        algo = keys[0]
        structure = keys[1] if len(keys) > 1 else "all"
        grp = grp.sort_values("size")
        n = grp["size"].values.astype(float)
        t = grp["mean_ns"].values.astype(float)

        if len(n) < 2:
            continue

        # log-log slope
        log_slope, log_intercept = np.polyfit(_safe_log(n), _safe_log(t), 1)

        # try fitting each theoretical model
        best_model, best_r2, best_c = "unknown", -1e9, 1.0
        for label, fn, x in [
            ("n_log_n", _growth_nlogn, n),
            ("n2", _growth_n2, n),
            ("n", _growth_n, n),
        ]:
            try:
                popt, _ = curve_fit(fn, x, t, p0=[1.0], maxfev=5000)
                t_pred = fn(x, *popt)
                ss_res = np.sum((t - t_pred) ** 2)
                ss_tot = np.sum((t - np.mean(t)) ** 2)
                r2 = 1 - ss_res / (ss_tot + 1e-30)
                if r2 > best_r2:
                    best_r2 = r2
                    best_model = label
                    best_c = popt[0]
            except Exception:
                pass

        results.append({
            "algorithm": algo,
            "structure": structure,
            "best_fit_model": best_model,
            "fitted_constant": round(best_c, 6),
            "r_squared": round(best_r2, 4),
            "log_log_slope": round(log_slope, 4),
        })

    return pd.DataFrame(results)


def fit_graph(df: pd.DataFrame) -> pd.DataFrame:
    """Fit timing data for graph algorithms."""
    results = []
    group_cols = ["algorithm", "graph_type"]

    for (algo, gtype), grp in df.groupby(group_cols):
        grp = grp.sort_values("V")
        v = grp["V"].values.astype(float)
        e = grp["E"].values.astype(float)
        t = grp["mean_ns"].values.astype(float)

        if len(v) < 2:
            continue

        log_slope, _ = np.polyfit(_safe_log(v), _safe_log(t + 1), 1)

        ve_logv = v * np.log2(np.maximum(v, 2)) + e
        ve = v * e

        best_model, best_r2, best_c = "unknown", -1e9, 1.0
        for label, fn, x in [
            ("V_logV_E", _growth_vlogv_e, ve_logv),
            ("V2", _growth_v2, v),
            ("VE", _growth_ve, ve),
        ]:
            try:
                popt, _ = curve_fit(fn, x, t, p0=[1.0], maxfev=5000)
                t_pred = fn(x, *popt)
                ss_res = np.sum((t - t_pred) ** 2)
                ss_tot = np.sum((t - np.mean(t)) ** 2)
                r2 = 1 - ss_res / (ss_tot + 1e-30)
                if r2 > best_r2:
                    best_r2 = r2
                    best_model = label
                    best_c = popt[0]
            except Exception:
                pass

        results.append({
            "algorithm": algo,
            "graph_type": gtype,
            "best_fit_model": best_model,
            "fitted_constant": round(best_c, 6),
            "r_squared": round(best_r2, 4),
            "log_log_slope": round(log_slope, 4),
        })

    return pd.DataFrame(results)
