# Last-Mile Delivery Dispatch: Algorithmic Benchmarking Project

**Course:** Design and Analysis of Algorithms (CS-312 / CLO-4)  
**Institution:** School of Electrical Engineering and Computer Science (SEECS), National University of Sciences and Technology (NUST)  
**Authors:**
- **Muhammad Arshyan** (CMS ID: `462685`)
- **Tahir Mehmood** (CMS ID: `458593`)

---

## 1. Executive Summary & Problem Scenario

In the twin-city metropolitan region of Islamabad and Rawalpindi, courier hubs (e.g., Islamabad I-9 Industrial Area, Rawalpindi Saddar) process high volumes of delivery consignments daily. The logistics pipeline faces two interdependent computational bottlenecks:

1. **Large-Scale Multi-Attribute Order Dispatching:** Batches of delivery orders ($n = 10^3$ to $10^6$) must be sorted under strict delivery deadlines, discrete priority tiers (1 = Urgent to 5 = Economy), parcel weights, and postal zone identifiers. A critical requirement is preserving **algorithm stability** when sorting on composite keys `(priority, deadline)` to ensure fair FIFO dispatch within equal priority tiers.
2. **Single-Source Shortest Path (SSSP) Route Navigation:** Fleet couriers navigate road networks modeled as directed weighted graphs where vertices represent intersections and edges represent travel times in minutes. The network evaluates two realistic topologies:
   - **Sparse Planar Sector Grids ($E \approx 3\text{--}5V$):** Modeling Islamabad's planned sector road network (Sectors F, G, H, I) with bounded vertex degrees.
   - **Dense Arterial Networks ($E \approx V^2 / 4$):** Modeling high-capacity highway expressways, bypasses, and multi-hub interchanges.
   - **Negative Weight Regimes:** Municipal green-corridor toll credits and congestion rebates introduce negative edge weights without creating negative cycles (guaranteed via potential-based reweighting: $w'(u, v) = w(u, v) + h(u) - h(v)$), along with controlled negative cycle injection to benchmark cycle detection.

All datasets are generated deterministically using a fixed global seed (`GLOBAL_SEED = 2024`) with MurmurHash3-derived per-dataset seeds, ensuring 100% scientific reproducibility.

---

## 2. Complete Project Structure & Output Organization

The repository is organized following modular software engineering principles. Below is the complete structural layout detailing where every component, source module, test, and generated output artifact is placed:

```
algo_eval/
├── README.md                      # Complete project documentation and output guide
├── requirements.txt               # Pinned dependencies (numpy, pandas, matplotlib, psutil, pytest, scipy)
├── run_all.py                     # Unified benchmark runner & evaluation pipeline CLI
├── generate_pdf_report.py         # Automated 14-page academic evaluation report PDF compiler
├── make_submission.py             # Packaging script creating verified submission.zip
├── DAA_CLO4_Evaluation_Report.pdf # Standalone 14-page university evaluation report
├── .gitignore                     # Cleanly ignores __pycache__, .pytest_cache, .pyc, and packaging archives
│
├── src/                           # Core implementation source code
│   ├── sorting/                   # Implemented-from-scratch sorting algorithms
│   │   ├── insertion_sort.py      # Quadratic baseline with O(n) early exit on sorted inputs
│   │   ├── merge_sort.py          # Top-down with pre-allocated reusable auxiliary buffer (stable)
│   │   ├── quick_sort.py          # Iterative stack-safe Hoare randomized & naive Lomuto variants
│   │   ├── heap_sort.py           # In-place Floyd's sift-down construction and extraction
│   │   ├── radix_sort.py          # Non-comparison LSD Base-256 stable counting sort on integer zone keys
│   │   └── __init__.py            # Sorting algorithm registry & quadratic size caps
│   │
│   ├── graphs/                    # Implemented-from-scratch SSSP graph algorithms
│   │   ├── graph.py               # Adjacency list directed graph representation
│   │   ├── dijkstra_heap.py       # Min-heap frontier via heapq with lazy deletion & safety cap
│   │   ├── dijkstra_array.py      # Flat distance array with O(V) scan per vertex (O(V^2))
│   │   ├── bellman_ford.py        # Dynamic programming edge-list relaxation with early exit & cycle detection
│   │   ├── spfa.py                # Shortest Path Faster Algorithm queue-based relaxation
│   │   └── __init__.py            # Graph algorithm registry & dense size caps
│   │
│   ├── generators/                # Deterministic synthetic data generators
│   │   ├── orders.py              # Order consignment records (deadlines, priorities, weights, zones)
│   │   └── graphs.py              # Road networks (sparse grids, dense expressways, potential reweighting)
│   │
│   ├── benchmark/                 # Isolated measurement & profiling harness
│   │   ├── timing.py              # High-precision time.perf_counter_ns with disabled GC isolation
│   │   ├── memory.py              # Untimed tracemalloc peak heap & psutil RSS delta tracking
│   │   ├── counters.py            # Hardware-independent operation counting (comparisons, swaps, relaxations)
│   │   └── runner.py              # Experiment runner orchestrating batches with incremental CSV checkpointing
│   │
│   ├── analysis/                  # Analysis, scoring, and regression fitting
│   │   ├── criteria.py            # Pre-set weights (summing to 100) & qualitative scoring matrices
│   │   ├── scoring.py             # Min-max normalization & multi-criteria weighted scoring engine
│   │   ├── fitting.py             # Asymptotic curve fitting (SciPy) & log-log slope regression
│   │   ├── sensitivity.py         # 1,000-trial Dirichlet Monte Carlo perturbation analysis
│   │   └── observations.py        # Automated gap detection and anomaly report generator
│   │
│   └── reporting/                 # Tabular and graphical report rendering
│       ├── tables.py              # Automated Markdown and LaTeX table generation
│       └── figures.py             # Publication-quality 300 DPI PNG & vector SVG chart generator
│
├── tests/                         # Unit and property test suite (39 passing tests)
│   ├── conftest.py                # Shared fixtures and deterministic test seeds
│   ├── test_sorting.py            # Correctness, stability, empty/single/duplicate/reverse cases
│   └── test_graphs.py             # Shortest paths vs brute force, negative cycles, potential reweighting
│
├── report_templates/              # Markdown report scaffolds and proof documentation
│   ├── contribution_statement.md  # Detailed work breakdown for group members
│   ├── recurrence_worked_examples.md # Master Theorem Case 2 and recursion tree proofs
│   └── report_outline.md          # Full academic report draft scaffold
│
└── output/                        # All benchmark output datasets, logs, tables, and figures
    ├── DAA_CLO4_Evaluation_Report.pdf # 14-page comprehensive university evaluation report
    │
    ├── [Raw Measurement Data]
    │   ├── raw_sorting.csv        # 1,169 recorded trials across all sizes, structures, and repeats
    │   └── raw_graph.csv          # Multi-repeat graph benchmarks across sparse, dense, and negative modes
    │
    ├── [Statistical Summaries]
    │   ├── summary_sorting.csv    # Aggregated mean, std, min, median runtime, memory, and speedups
    │   └── summary_graph.csv      # Aggregated graph metrics across topologies and weight regimes
    │
    ├── [Multi-Criteria Scoring & Sensitivity]
    │   ├── scores_sorting.csv     # Pre-registered weighted scores and rankings for sorting algorithms
    │   ├── scores_graph.csv       # Pre-registered weighted scores and rankings for graph algorithms
    │   ├── sensitivity_analysis.csv # 1,000-trial Dirichlet Monte Carlo ranking stability distribution
    │   ├── sensitivity_analysis_sorting.csv # Detailed sorting sensitivity statistics
    │   └── sensitivity_analysis_graph.csv   # Detailed graph sensitivity statistics
    │
    ├── [Asymptotic Regression & Complexity]
    │   ├── fit_results.csv        # Empirical log-log regression exponents (alpha), constants, and R^2
    │   ├── fit_results_sorting.csv # Sorting-specific curve fitting models
    │   ├── fit_results_graph.csv   # Graph-specific curve fitting models
    │   ├── complexity_table.csv   # Theoretical complexity benchmark table (CSV format)
    │   └── complexity_table.md    # Theoretical complexity benchmark table (Markdown format)
    │
    ├── [Environment & Diagnostics]
    │   ├── environment.json       # Host hardware (CPU model, physical cores, RAM), OS, Python/library versions
    │   ├── correctness_and_stability_report.txt # Automated observations and empirical discrepancy notes
    │   └── dijkstra_negative_weight_failures.csv # Discrepancy log documenting Dijkstra collapse on negative edges
    │
    ├── logs/                      # Execution trace logs
    │   └── run.log                # Timestamped step-by-step pipeline execution log
    │
    ├── tables/                    # Exported LaTeX (.tex) and Markdown (.md) formatted tables
    │   ├── summary_sorting.md / .tex
    │   ├── summary_graph.md / .tex
    │   ├── scores_sorting.md / .tex
    │   ├── scores_graph.md / .tex
    │   ├── fit_results.md / .tex
    │   ├── sensitivity_analysis.md / .tex
    │   └── complexity_table.md / .tex
    │
    └── figures/                   # 21 publication-quality 300 DPI PNG & vector SVG chart pairs
        ├── runtime_loglog_sorting_random.png / .svg
        ├── runtime_loglog_sorting_sorted.png / .svg
        ├── runtime_loglog_sorting_reverse_sorted.png / .svg
        ├── runtime_loglog_sorting_nearly_sorted.png / .svg
        ├── runtime_loglog_sorting_many_duplicates.png / .svg
        ├── runtime_loglog_sorting_composite.png / .svg
        ├── runtime_loglog_sorting_integer_zone.png / .svg
        ├── runtime_loglog_graph_all.png / .svg
        ├── memory_sorting.png / .svg
        ├── memory_graph.png / .svg
        ├── sparse_vs_dense_graph.png / .svg
        ├── crossover_insertion_vs_merge.png / .svg
        ├── operation_counts_sorting.png / .svg
        ├── time_theory_ratio_sorting.png / .svg
        ├── time_theory_ratio_graph.png / .svg
        ├── weighted_scores_sorting.png / .svg
        ├── weighted_scores_graph.png / .svg
        ├── stacked_contributions_sorting.png / .svg
        ├── stacked_contributions_graph.png / .svg
        ├── sensitivity_heatmap_sorting.png / .svg
        └── sensitivity_heatmap_graph.png / .svg
```

---

## 3. Implemented Algorithms & Techniques

All algorithms are implemented from scratch in Python 3.10+ without using third-party algorithmic packages:

### 3.1 Sorting Algorithms (`src/sorting/`)

| Algorithm | Average Time | Worst Time | Space | Stable | Implementation Technique & Mechanics |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Insertion Sort** | $O(n^2)$ | $O(n^2)$ | $O(1)$ | Yes | In-place incremental insertion with linear scan. Exhibits $O(n)$ early exit on sorted inputs. Capped at $n = 10,000$. |
| **Merge Sort** | $O(n \log n)$ | $O(n \log n)$ | $O(n)$ | Yes | Top-down divide-and-conquer using a **single pre-allocated reusable auxiliary buffer** to eliminate recurring allocation overhead and strictly maintain stability. |
| **Quick Sort (Hoare + Random)** | $O(n \log n)$ | $O(n^2)^*$ | $O(\log n)$ | No | **Iterative stack-safe implementation** with randomized pivot selection and dual-pointer Hoare partitioning. Swapping equal keys avoids $O(n^2)$ clustering on heavy duplicate inputs. |
| **Quick Sort (Naive First-Pivot)** | $O(n \log n)$ | $O(n^2)$ | $O(n)$ | No | Fixed first-element Lomuto partition. Capped at $n = 10,000$ to empirically demonstrate quadratic degeneration on sorted/reverse-sorted inputs. |
| **Heap Sort** | $O(n \log n)$ | $O(n \log n)$ | $O(1)$ | No | Completely in-place array transformation using Floyd's sift-down build-heap in $O(n)$ time followed by $n-1$ max-heap extraction and sift-down passes. |
| **Radix Sort (LSD Base-256)** | $O(d \cdot n)$ | $O(d \cdot n)$ | $O(n + k)$ | Yes | Non-comparison Least Significant Digit (LSD) counting sort on 32-bit integer zone keys using 4 passes (base $2^{8} = 256$) with stable reverse-bucket placement. |
| **Timsort** *(Python Reference)* | $O(n \log n)$ | $O(n \log n)$ | $O(n)$ | Yes | Standard library `sorted()` included as a compiled C external performance reference baseline. |

*\*Worst-case $O(n^2)$ occurs with negligible probability $O(1/n!)$ under random pivoting.*

### 3.2 SSSP Graph Algorithms (`src/graphs/`)

| Algorithm | Asymptotic Complexity | Space | Negative Weights | Negative Cycles | Implementation Technique & Mechanics |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Dijkstra (Binary Heap)** | $O((V + E) \log V)$ | $O(V + E)$ | No | No | Min-heap frontier via Python's `heapq` with lazy deletion (ignoring stale entries) and an iteration safety cap to prevent infinite cycling on negative cycles. |
| **Dijkstra (Flat Array)** | $O(V^2)$ | $O(V)$ | No | No | Flat distance array with $O(V)$ unvisited linear scans per vertex extraction. Optimal for dense arterial networks ($E \approx V^2 / 4$). |
| **Bellman-Ford** | $O(V \cdot E)$ | $O(V)$ | Yes | Yes | Dynamic programming edge-list relaxation with **early termination** if an iteration produces 0 relaxations, and negative cycle detection on the $V$-th pass. |
| **SPFA** | $O(k \cdot E)$ avg | $O(V)$ | Yes | Yes | Shortest Path Faster Algorithm using a FIFO queue and an `in_queue` boolean array to relax only vertices whose labels decreased. |

---

## 4. Pre-Set Evaluation Criteria & Scoring Framework

To eliminate post-hoc evaluation bias, all criteria and percentage weights (summing strictly to 100 per domain) were formally registered in `src/analysis/criteria.py` prior to benchmark execution:

```
Sorting Criteria (Total = 100):
├── Measured Runtime:        30% (Relative speedup vs baseline)
├── Theoretical Complexity:  15% (Worst/average case bound)
├── Auxiliary Memory:        15% (Peak tracemalloc heap allocation)
├── Stability:               15% (Preservation of equal-key order)
├── Input Robustness:        15% (Coefficient of variation across structures)
└── Key Type Suitability:    10% (Versatility across floats, composites, integers)

Graph Criteria (Total = 100):
├── Measured Runtime:        30% (Average execution latency)
├── Scalability (Dense/Sparse): 15% (Performance shift from grid to dense)
├── Negative Weight Safety:  20% (Correctness on toll credits & cycle detection)
├── Theoretical Complexity:  15% (Asymptotic upper bound)
├── Auxiliary Memory:        10% (Peak memory footprint)
└── Simplicity:              10% (Code maintainability and implementation ease)
```

### Empirical Rankings & Sensitivity Analysis
- **Sorting Overall Ranking:** Timsort (82.03, Rank 1), Radix Sort (80.69, Rank 2), Heap Sort (75.74, Rank 3), Quick Sort Hoare (73.34, Rank 4), Merge Sort (63.98, Rank 5), Insertion Sort (40.35, Rank 6), Naive Quick Sort (33.21, Rank 7).
- **Graph Overall Ranking:** Dijkstra Array (69.75, Rank 1), Dijkstra Heap (66.75, Rank 2), SPFA (52.53, Rank 3), Bellman-Ford (35.00, Rank 4).
- **1,000-Trial Dirichlet Sensitivity Analysis:** Under random Dirichlet perturbations $w \sim \operatorname{Dirichlet}(\alpha) \times 100$, Timsort ranked 1st in 47.7% of trials, Heap Sort in 25.2%, and Radix Sort in 17.1%. For graphs, Dijkstra Heap ranked 1st in 54.3% of trials (dominating sparse planar networks), SPFA in 27.0%, and Dijkstra Array in 9.2%.

---

## 5. Empirical Benchmarks & Theory-vs-Measurement Highlights

1. **Presorted Data Inversion:** Insertion Sort achieved $O(n)$ linear scaling ($\alpha = 1.14$, $R^2 = 0.998$, $0.95\text{ ms}$ at $n = 10,000$) on sorted data, but degraded to $O(n^2)$ ($\alpha = 2.28$, $R^2 = 1.000$, $231.5\text{ s}$) on reverse-sorted inputs.
2. **Lomuto Partition Degradation:** Naive Quick Sort with Lomuto partitioning degraded to $O(n^2)$ ($\alpha = 1.75$, $R^2 = 0.999$) on duplicate-heavy priority inputs because equal keys clustered on one side. Our iterative Hoare dual-pointer partition fixed this, achieving balanced splits in $O(n \log n)$ time.
3. **Cache Locality Crossover:** For $n \le 1,000$, Insertion Sort outperformed Merge Sort due to contiguous in-place L1/L2 cache prefetching. Merge Sort overtook Insertion Sort at $n \approx 1,000$ and achieved a $15\times$ speedup at $n = 10,000$.
4. **Dense vs. Sparse Graph Inversion:** On sparse planar grids ($E \approx 4V$), Dijkstra (Heap) ran in $3.25\text{ ms}$ ($O(V \log V)$), outperforming Array Dijkstra ($17.74\text{ ms}$). On dense arterial networks ($E \approx V^2 / 4$), Array Dijkstra dominated ($0.51\times$ dense/sparse ratio) because heap management overhead ($O(V^2 \log V)$ pushes) exceeded flat $O(V^2)$ array scans.
5. **Dijkstra Collapse on Negative Weights:** On potential-reweighted safe graphs, greedy relabeling failed, corrupting $14\text{--}38\%$ of distance labels (recorded in `output/dijkstra_negative_weight_failures.csv`). Bellman-Ford and SPFA maintained 100% accuracy and successfully flagged negative 3-cycles.

---

## 6. Algorithmic Recommendations & Defenses

- **Dispatch Order Sorting:** **Merge Sort** is recommended. While Quick Sort has lower memory overhead ($O(\log n)$ vs $O(n)$) and lower constant factors, Quick Sort is **unstable**. Sorting dispatch consignments by composite keys `(priority, deadline)` requires stability to preserve customer submission order within identical priority tiers. Merge Sort guarantees strict stability and deterministic $O(n \log n)$ performance across all input distributions.
- **Road Network SSSP Routing:** **Dijkstra's Algorithm with Binary Min-Heap** is recommended. Metropolitan road networks in Islamabad/Rawalpindi are sparse planar networks ($E \approx 4V$), where Heap Dijkstra operates in $3.25\text{ ms}$ ($O(V \log V)$), vastly outperforming Array Dijkstra ($17.74\text{ ms}$) and Bellman-Ford ($584.06\text{ ms}$). To handle toll rebates or green incentives, the routing service incorporates an automatic fallback to SPFA ($417.92\text{ ms}$).

---

## 7. Reproduction Guide

### Setup & Dependencies
```powershell
# Clone the repository
git clone https://github.com/arshyan11/DAA-Assignment2.git
cd DAA-Assignment2

# Install required dependencies
pip install -r requirements.txt
```

### Running the Test Suite
```powershell
# Run the complete pytest test suite (39/39 passing tests)
pytest tests/ -v
```

### Running the Benchmark Suite
```powershell
# Quick mode (~5-10 minutes, verifies all structures, generates all figures and tables)
python run_all.py --quick

# Full mode (evaluates up to 10^6 elements and large graphs)
python run_all.py --full

# Resume execution from checkpoint after interruption
python run_all.py --quick --resume

# Re-compile the comprehensive 14-page evaluation report PDF
python generate_pdf_report.py
```

---

## 8. Individual Contribution Statement

- **Muhammad Arshyan (CMS ID: `462685`, Lead System Architect):**
  1. Authored Merge Sort with reusable buffer, Iterative Randomized Quick Sort with Hoare partitioning, and Radix Sort (LSD Base-256).
  2. Engineered timing harness with automated garbage-collection isolation and dual-pass tracemalloc/psutil memory tracking.
  3. Formulated formal Master Theorem Case 2 and recursion tree proofs for Merge Sort and Quick Sort.
  4. Implemented multi-criteria normalization models and the 1,000-trial Dirichlet Monte Carlo sensitivity analysis.
- **Tahir Mehmood (CMS ID: `458593`, Lead Graph & Empirical Analyst):**
  1. Implemented Dijkstra with Binary Min-Heap (lazy deletion), Dijkstra with Flat Array, Bellman-Ford with early exit, and SPFA.
  2. Engineered synthetic dataset generators for delivery order consignments and road networks (sparse sector grids, dense expressways, potential-reweighted negative edges, and cycle injection).
  3. Conducted negative-weight vulnerability tests, logging corrupted distance labels and cycle detection flags.
  4. Developed matplotlib visualization pipeline (generating all 21 publication figures) and automated LaTeX table generation.
- **Joint Collaborative Work:** Logistics scenario modeling, pre-experiment criteria weighting, test suite validation, and report review.
