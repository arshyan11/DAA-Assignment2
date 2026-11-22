# Recurrence Worked Examples

These derivations can be adapted for the report. Write in your own voice.

---

## 1. Merge Sort: T(n) = 2T(n/2) + O(n)

### Master Theorem (Case 2)

The recurrence for merge sort is:

    T(n) = 2T(n/2) + cn

where c is the constant cost of the merge step per element.

Identify parameters for the Master Theorem T(n) = aT(n/b) + f(n):
- a = 2  (two recursive subproblems)
- b = 2  (each subproblem is half the size)
- f(n) = cn  (the merge operation)

Compute: log_b(a) = log_2(2) = 1

Compare f(n) = O(n) with n^(log_b(a)) = n^1 = n.

Since f(n) = Theta(n^1) = Theta(n^(log_b(a))), this is **Case 2** of the Master Theorem:

    T(n) = Theta(n^(log_b(a)) * log n) = Theta(n log n)

### Recursion Tree Verification

Level 0: 1 problem of size n, merge cost = cn
Level 1: 2 problems of size n/2, merge cost = 2 * c(n/2) = cn
Level 2: 4 problems of size n/4, merge cost = 4 * c(n/4) = cn
...
Level k: 2^k problems of size n/2^k, merge cost = cn

The tree has log_2(n) levels (stops when n/2^k = 1, so k = log_2(n)).

Total cost = cn * (number of levels) = cn * log_2(n) = Theta(n log n).

This matches the Master Theorem result.

---

## 2. Quick Sort Recurrences

### Best Case: T(n) = 2T(n/2) + O(n)

When every pivot splits the array exactly in half, the recurrence is identical
to merge sort. By the Master Theorem Case 2: T(n) = Theta(n log n).

### Worst Case: T(n) = T(n-1) + O(n)

When the pivot is always the smallest or largest element (e.g., first-pivot
on sorted input), we get:

    T(n) = T(n-1) + cn

Expanding:
    T(n) = cn + c(n-1) + c(n-2) + ... + c(1)
         = c * [n + (n-1) + (n-2) + ... + 1]
         = c * n(n+1)/2
         = Theta(n^2)

This is confirmed empirically by the quick_sort_naive variant on sorted input.

### Average Case: T(n) = (1/n) * sum_{q=0}^{n-1} [T(q) + T(n-1-q)] + O(n)

After simplification (omitted here; see CLRS Section 7.4.2):

    T(n) = O(n log n)

The average case matches the best case in asymptotic order.

---

## 3. Dijkstra with Binary Heap: O((V + E) log V)

Building the initial heap takes O(V) time.

Each vertex is extracted from the min-heap exactly once: V extract-min
operations, each taking O(log V). Total: O(V log V).

Each edge (u, v) is relaxed at most once. If the relaxation succeeds, a
decrease-key (or lazy insert) takes O(log V). Over all edges: O(E log V).

Total: O(V log V + E log V) = O((V + E) log V).

On sparse graphs where E = O(V), this is O(V log V).
On dense graphs where E = O(V^2), this is O(V^2 log V), which is worse than
the plain O(V^2) array-based Dijkstra. This explains the crossover we see
in the benchmark data for dense graphs.

---

## 4. Bellman-Ford: O(V * E)

The outer loop runs at most V-1 times (or fewer with early exit).
Each iteration scans all E edges and attempts a relaxation.

Worst case: O(V * E).

With early exit: if no relaxation happens in an iteration, the algorithm
terminates early. On sparse graphs with positive weights, this often
converges in far fewer than V-1 iterations, explaining why measured
runtime is better than the theoretical O(V * E) bound.

The additional negative-cycle detection pass scans all E edges once more,
adding O(E) but not changing the asymptotic bound.
