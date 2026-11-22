# Theoretical Complexity

| Algorithm | Best Time | Average Time | Worst Time | Space | Stable |
| --- | --- | --- | --- | --- | --- |
| Insertion Sort | O(n) | O(n^2) | O(n^2) | O(1) | Yes |
| Merge Sort | O(n log n) | O(n log n) | O(n log n) | O(n) | Yes |
| Quick Sort (random pivot) | O(n log n) | O(n log n) | O(n^2)* | O(log n) | No |
| Quick Sort (naive pivot) | O(n) | O(n log n) | O(n^2) | O(log n) | No |
| Heap Sort | O(n log n) | O(n log n) | O(n log n) | O(1) | No |
| Radix Sort (LSD) | O(d*n) | O(d*n) | O(d*n) | O(n+k) | Yes |
| Timsort (reference) | O(n) | O(n log n) | O(n log n) | O(n) | Yes |
| Dijkstra (heap) | O((V+E) log V) | O((V+E) log V) | O((V+E) log V) | O(V+E) | N/A |
| Dijkstra (array) | O(V^2) | O(V^2) | O(V^2) | O(V) | N/A |
| Bellman-Ford | O(E) | O(V*E) | O(V*E) | O(V+E) | N/A |
| SPFA | O(E) avg | O(k*E) | O(V*E) | O(V+E) | N/A |

