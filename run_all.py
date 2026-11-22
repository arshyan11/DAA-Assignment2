"""Main CLI entry point: run_all.py - orchestrates all benchmark experiments."""

import argparse
import gc
import json
import logging
import os
import platform
import sys
import time
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT.parent))

from algo_eval.src.sorting import SORT_REGISTRY
from algo_eval.src.graphs import GRAPH_REGISTRY
from algo_eval.src.generators.orders import generate_orders, SORT_KEYS, STRUCTURES
from algo_eval.src.generators.graphs import (
    make_sparse_grid_graph,
    make_dense_graph,
    graph_sizes_sparse,
    graph_sizes_dense,
    WEIGHT_MODES,
)
from algo_eval.src.benchmark.runner import run_sorting_experiments, run_graph_experiments
from algo_eval.src.reporting.tables import (
    summarise_sorting,
    summarise_graph,
    complexity_table,
    write_markdown_table,
    write_latex_table,
    write_dijkstra_failures,
)


GLOBAL_SEED = 2024

SIZES_QUICK = [1_000, 5_000, 10_000, 50_000]
SIZES_FULL = [1_000, 5_000, 10_000, 50_000, 100_000, 500_000, 1_000_000]

GRAPH_SPARSE_QUICK = [(10, 10), (22, 22), (31, 32)]
GRAPH_DENSE_QUICK = [100, 500]


def setup_logging(output_dir: Path) -> None:
    log_dir = output_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "run.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def collect_environment(output_dir: Path, seed: int, size_caps: dict) -> None:
    """Write environment.json with machine and run metadata."""
    try:
        import psutil
        ram_gb = round(psutil.virtual_memory().total / 1e9, 1)
        cpu_model = platform.processor() or "unknown"
        core_count = psutil.cpu_count(logical=False)
    except Exception:
        ram_gb = "unknown"
        cpu_model = platform.processor()
        core_count = "unknown"

    import numpy, pandas, matplotlib
    env = {
        "python_version": sys.version,
        "os": platform.platform(),
        "cpu_model": cpu_model,
        "cpu_cores_physical": core_count,
        "ram_gb": ram_gb,
        "numpy_version": numpy.__version__,
        "pandas_version": pandas.__version__,
        "matplotlib_version": matplotlib.__version__,
        "global_seed": seed,
        "run_date": datetime.now().isoformat(),
        "size_caps": size_caps,
        "notes": (
            "O(n^2) algorithms (insertion_sort, quick_sort_naive) are capped at their "
            "quadratic_cap sizes defined in src/sorting/__init__.py. "
            "Dense graphs skip large V for Dijkstra variants per dense_cap in "
            "src/graphs/__init__.py. All other algorithms run at all listed sizes."
        ),
    }
    with open(output_dir / "environment.json", "w") as f:
        json.dump(env, f, indent=2)
    logging.getLogger(__name__).info("environment.json written")


def run_report(output_dir: Path) -> None:
    """Generate summary CSVs, tables, figures, scoring, sensitivity, observations."""
    import pandas as pd
    from algo_eval.src.analysis.criteria import SORTING_WEIGHTS, GRAPH_WEIGHTS
    from algo_eval.src.analysis.scoring import score_sorting, score_graph
    from algo_eval.src.analysis.fitting import fit_sorting, fit_graph
    from algo_eval.src.analysis.sensitivity import run_sensitivity, fixed_perturbation_analysis
    from algo_eval.src.analysis.observations import generate_observations
    from algo_eval.src.reporting import figures as fig_mod

    logger = logging.getLogger(__name__)
    tables_dir = output_dir / "tables"
    figures_dir = output_dir / "figures"
    tables_dir.mkdir(exist_ok=True)
    figures_dir.mkdir(exist_ok=True)

    raw_sort = output_dir / "raw_sorting.csv"
    raw_graph = output_dir / "raw_graph.csv"
    sum_sort = output_dir / "summary_sorting.csv"
    sum_graph = output_dir / "summary_graph.csv"

    sort_summary = pd.DataFrame()
    graph_summary = pd.DataFrame()

    if raw_sort.exists():
        logger.info("Building sorting summary...")
        sort_summary = summarise_sorting(raw_sort, sum_sort)
        write_markdown_table(sort_summary, tables_dir / "summary_sorting.md", "Sorting Summary Statistics")
        write_latex_table(sort_summary, tables_dir / "summary_sorting.tex",
                          "Sorting Summary Statistics", "tab:sorting_summary")
    if raw_graph.exists():
        logger.info("Building graph summary...")
        graph_summary = summarise_graph(raw_graph, sum_graph)
        write_markdown_table(graph_summary, tables_dir / "summary_graph.md", "Graph Summary Statistics")
        write_latex_table(graph_summary, tables_dir / "summary_graph.tex",
                          "Graph Summary Statistics", "tab:graph_summary")

    # complexity table
    ct = complexity_table()
    ct.to_csv(output_dir / "complexity_table.csv", index=False)
    write_markdown_table(ct, output_dir / "complexity_table.md", "Theoretical Complexity")
    write_markdown_table(ct, tables_dir / "complexity_table.md", "Theoretical Complexity")
    write_latex_table(ct, tables_dir / "complexity_table.tex",
                      "Theoretical Complexity of All Algorithms", "tab:complexity")

    if not sort_summary.empty:
        logger.info("Scoring and sensitivity for sorting...")

        def _sort_score_fn(df, weights):
            from algo_eval.src.analysis.scoring import _minmax_score
            from algo_eval.src.analysis.criteria import (
                STABILITY_SCORES, DATA_SUITABILITY_SCORES, THEORETICAL_COMPLEXITY_SORT
            )
            g = df.groupby("algorithm").agg(mean_ns=("mean_ns", "mean"),
                                             peak_mem_bytes=("peak_mem_bytes", "mean")).reset_index()
            g["runtime_score"] = _minmax_score(g["mean_ns"])
            g["memory_score"] = _minmax_score(g["peak_mem_bytes"])
            g["stability_score"] = g["algorithm"].map(STABILITY_SCORES).fillna(0)
            g["theory_score"] = g["algorithm"].map(THEORETICAL_COMPLEXITY_SORT).fillna(0)
            g["suitability_score"] = g["algorithm"].map(DATA_SUITABILITY_SCORES).fillna(0)
            g["robustness_score"] = 5.0
            g["weighted_total"] = (
                g["runtime_score"] * weights.get("measured_runtime", 30)
                + g["theory_score"] * weights.get("theoretical_complexity", 15)
                + g["memory_score"] * weights.get("memory", 15)
                + g["stability_score"] * weights.get("stability", 15)
                + g["robustness_score"] * weights.get("input_robustness", 15)
                + g["suitability_score"] * weights.get("data_type_suitability", 10)
            ) / 10.0
            return g

        scores_sort = score_sorting(sort_summary)
        scores_sort.to_csv(output_dir / "scores_sorting.csv", index=False)
        write_markdown_table(scores_sort, tables_dir / "scores_sorting.md", "Sorting Algorithm Rankings")
        write_latex_table(scores_sort, tables_dir / "scores_sorting.tex",
                          "Sorting Algorithm Rankings", "tab:scores_sorting")

        sensitivity_sort = run_sensitivity(sort_summary, SORTING_WEIGHTS, _sort_score_fn, n_trials=1000)
        sensitivity_sort.to_csv(output_dir / "sensitivity_analysis_sorting.csv", index=False)
        write_markdown_table(sensitivity_sort, tables_dir / "sensitivity_sorting.md", "Sorting Sensitivity")

        fixed_sort = fixed_perturbation_analysis(sort_summary, SORTING_WEIGHTS, _sort_score_fn)
        fixed_sort.to_csv(output_dir / "sensitivity_fixed_sorting.csv", index=False)

        fit_sort = fit_sorting(sort_summary)
        fit_sort.to_csv(output_dir / "fit_results_sorting.csv", index=False)

        # figures
        fig_mod.plot_runtime_loglog(sort_summary, figures_dir, task="sorting")
        fig_mod.plot_memory(sort_summary, figures_dir, task="sorting")
        fig_mod.plot_weighted_scores(scores_sort, figures_dir, task="sorting")
        fig_mod.plot_stacked_contributions(scores_sort, figures_dir, task="sorting")
        fig_mod.plot_time_theory_ratio(sort_summary, figures_dir, task="sorting")
        fig_mod.plot_operation_counts(sort_summary, figures_dir)
        fig_mod.plot_stability_demo(sort_summary, figures_dir)
        fig_mod.plot_crossover(sort_summary, figures_dir)
        fig_mod.plot_sensitivity_heatmap(sensitivity_sort, figures_dir, task="sorting")

    if not graph_summary.empty:
        logger.info("Scoring and sensitivity for graphs...")

        def _graph_score_fn(df, weights):
            from algo_eval.src.analysis.scoring import _minmax_score
            from algo_eval.src.analysis.criteria import (
                NEGATIVE_WEIGHT_CORRECTNESS, THEORETICAL_COMPLEXITY_GRAPH, IMPLEMENTATION_SIMPLICITY
            )
            g = df.groupby("algorithm").agg(mean_ns=("mean_ns", "mean"),
                                             peak_mem_bytes=("peak_mem_bytes", "mean")).reset_index()
            g["runtime_score"] = _minmax_score(g["mean_ns"])
            g["memory_score"] = _minmax_score(g["peak_mem_bytes"])
            g["neg_weight_score"] = g["algorithm"].map(NEGATIVE_WEIGHT_CORRECTNESS).fillna(0)
            g["theory_score"] = g["algorithm"].map(THEORETICAL_COMPLEXITY_GRAPH).fillna(0)
            g["simplicity_score"] = g["algorithm"].map(IMPLEMENTATION_SIMPLICITY).fillna(0)
            g["scalability_score"] = 5.0
            g["weighted_total"] = (
                g["runtime_score"] * weights.get("measured_runtime", 30)
                + g["theory_score"] * weights.get("theoretical_complexity", 15)
                + g["memory_score"] * weights.get("memory", 10)
                + g["neg_weight_score"] * weights.get("correctness_negative", 20)
                + g["scalability_score"] * weights.get("scalability_sparse_dense", 15)
                + g["simplicity_score"] * weights.get("implementation_simplicity", 10)
            ) / 10.0
            return g

        scores_graph = score_graph(graph_summary)
        scores_graph.to_csv(output_dir / "scores_graph.csv", index=False)
        write_markdown_table(scores_graph, tables_dir / "scores_graph.md", "Graph Algorithm Rankings")
        write_latex_table(scores_graph, tables_dir / "scores_graph.tex",
                          "Graph Algorithm Rankings", "tab:scores_graph")

        sensitivity_graph = run_sensitivity(graph_summary, GRAPH_WEIGHTS, _graph_score_fn, n_trials=1000)
        sensitivity_graph.to_csv(output_dir / "sensitivity_analysis_graph.csv", index=False)
        write_markdown_table(sensitivity_graph, tables_dir / "sensitivity_graph.md", "Graph Sensitivity")

        fit_graph_df = fit_graph(graph_summary)
        fit_graph_df.to_csv(output_dir / "fit_results_graph.csv", index=False)

        fig_mod.plot_runtime_loglog(graph_summary, figures_dir, task="graph")
        fig_mod.plot_memory(graph_summary, figures_dir, task="graph")
        fig_mod.plot_weighted_scores(scores_graph, figures_dir, task="graph")
        fig_mod.plot_stacked_contributions(scores_graph, figures_dir, task="graph")
        fig_mod.plot_time_theory_ratio(graph_summary, figures_dir, task="graph")
        fig_mod.plot_sparse_vs_dense(graph_summary, figures_dir)
        fig_mod.plot_sensitivity_heatmap(sensitivity_graph, figures_dir, task="graph")

        write_dijkstra_failures(raw_graph, output_dir / "dijkstra_negative_weight_failures.csv")

    # combined sensitivity analysis
    all_sens = []
    if (output_dir / "sensitivity_analysis_sorting.csv").exists():
        all_sens.append(pd.read_csv(output_dir / "sensitivity_analysis_sorting.csv").assign(task="sorting"))
    if (output_dir / "sensitivity_analysis_graph.csv").exists():
        all_sens.append(pd.read_csv(output_dir / "sensitivity_analysis_graph.csv").assign(task="graph"))
    if all_sens:
        comb_sens = pd.concat(all_sens, ignore_index=True)
        comb_sens.to_csv(output_dir / "sensitivity_analysis.csv", index=False)
        write_markdown_table(comb_sens, tables_dir / "sensitivity_analysis.md", "Sensitivity Analysis")
        write_latex_table(comb_sens, tables_dir / "sensitivity_analysis.tex",
                          "Sensitivity Analysis", "tab:sensitivity_analysis")

    # combined fit results
    all_fits = []
    if (output_dir / "fit_results_sorting.csv").exists():
        all_fits.append(pd.read_csv(output_dir / "fit_results_sorting.csv").assign(task="sorting"))
    if (output_dir / "fit_results_graph.csv").exists():
        all_fits.append(pd.read_csv(output_dir / "fit_results_graph.csv").assign(task="graph"))
    if all_fits:
        comb_fits = pd.concat(all_fits, ignore_index=True)
        comb_fits.to_csv(output_dir / "fit_results.csv", index=False)
        write_markdown_table(comb_fits, tables_dir / "fit_results.md", "Curve Fitting Results")
        write_latex_table(comb_fits, tables_dir / "fit_results.tex",
                          "Curve Fitting Results", "tab:fit_results")

    # observations
    obs = generate_observations(sort_summary, graph_summary,
                                 pd.read_csv(output_dir / "fit_results.csv") if (output_dir / "fit_results.csv").exists() else pd.DataFrame(),
                                 pd.DataFrame())
    with open(output_dir / "correctness_and_stability_report.txt", "w") as f:
        f.write(obs)

    logger.info("Report generation complete. All outputs in %s", output_dir)


def main():
    parser = argparse.ArgumentParser(
        description="Last-mile delivery dispatch algorithm benchmark"
    )
    parser.add_argument("--quick", action="store_true", help="Run with small sizes (minutes)")
    parser.add_argument("--full", action="store_true", help="Run with all sizes (hours)")
    parser.add_argument(
        "--mode", choices=["quick", "full"], default="quick",
        help="'quick' uses small sizes (minutes); 'full' runs all sizes (hours)",
    )
    parser.add_argument(
        "--only", choices=["sorting", "graph", "report"],
        help="Run only sorting, only graph, or only the report/analysis phase",
    )
    parser.add_argument("--resume", action="store_true", help="Resume from existing CSV checkpoints")
    parser.add_argument("--seed", type=int, default=GLOBAL_SEED, help="Global random seed")
    parser.add_argument(
        "--output", type=str, default=str(ROOT / "output"),
        help="Directory to write all outputs",
    )
    args = parser.parse_args()

    chosen_mode = "full" if (args.full or args.mode == "full") and not args.quick else "quick"

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "figures").mkdir(exist_ok=True)
    (output_dir / "tables").mkdir(exist_ok=True)
    (output_dir / "logs").mkdir(exist_ok=True)

    setup_logging(output_dir)
    logger = logging.getLogger(__name__)
    logger.info("Starting benchmark | mode=%s seed=%d", chosen_mode, args.seed)

    seed = args.seed
    sizes = SIZES_QUICK if chosen_mode == "quick" else SIZES_FULL
    sparse_sizes = GRAPH_SPARSE_QUICK if chosen_mode == "quick" else graph_sizes_sparse()
    dense_sizes = GRAPH_DENSE_QUICK if chosen_mode == "quick" else graph_sizes_dense()

    size_caps = {
        name: info.get("quadratic_cap", "none")
        for name, info in SORT_REGISTRY.items()
    }
    collect_environment(output_dir, seed, size_caps)

    if args.only in (None, "sorting"):
        logger.info("Running sorting experiments...")
        run_sorting_experiments(
            algorithms=SORT_REGISTRY,
            sizes=sizes,
            structures=STRUCTURES,
            sort_keys=SORT_KEYS,
            generate_fn=generate_orders,
            output_path=output_dir / "raw_sorting.csv",
            global_seed=seed,
            repeats_small=7,
            repeats_large=3,
            large_threshold=100_000,
            resume=args.resume,
        )
        logger.info("Sorting experiments done.")

    if args.only in (None, "graph"):
        logger.info("Running graph experiments...")
        run_graph_experiments(
            algorithms=GRAPH_REGISTRY,
            sparse_sizes=sparse_sizes,
            dense_sizes=dense_sizes,
            weight_modes=WEIGHT_MODES,
            make_sparse_fn=make_sparse_grid_graph,
            make_dense_fn=make_dense_graph,
            output_path=output_dir / "raw_graph.csv",
            global_seed=seed,
            repeats_small=7,
            repeats_large=3,
            large_threshold=2000,
            resume=args.resume,
        )
        logger.info("Graph experiments done.")

    if args.only in (None, "report"):
        logger.info("Generating report assets...")
        try:
            run_report(output_dir)
        except Exception as e:
            logger.warning("Report generation failed: %s", e)
            import traceback
            traceback.print_exc()

    logger.info("All done. Outputs in: %s", output_dir)


if __name__ == "__main__":
    main()
