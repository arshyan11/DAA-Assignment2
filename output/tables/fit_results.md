# Curve Fitting Results

| algorithm | structure | best_fit_model | fitted_constant | r_squared | log_log_slope | task | graph_type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| heap_sort | composite | n_log_n | 1106.016266 | 0.9996 | 1.1139 | sorting |  |
| heap_sort | integer_zone | n_log_n | 855.976215 | 1.0 | 1.0857 | sorting |  |
| heap_sort | many_duplicates | n_log_n | 756.373711 | 1.0 | 1.0742 | sorting |  |
| heap_sort | nearly_sorted | n_log_n | 871.504999 | 0.9997 | 1.0897 | sorting |  |
| heap_sort | random | n_log_n | 859.63928 | 1.0 | 1.0924 | sorting |  |
| heap_sort | reverse_sorted | n_log_n | 840.143901 | 1.0 | 1.06 | sorting |  |
| heap_sort | sorted | n_log_n | 861.957484 | 0.9999 | 1.0711 | sorting |  |
| insertion_sort | composite | n | 720942.375385 | 0.9445 | 2.1048 | sorting |  |
| insertion_sort | integer_zone | n2 | 39.325526 | 0.9837 | 1.9801 | sorting |  |
| insertion_sort | many_duplicates | n | 9137.273786 | 0.8135 | 1.1086 | sorting |  |
| insertion_sort | nearly_sorted | n_log_n | 2379.626182 | 0.9898 | 1.5589 | sorting |  |
| insertion_sort | random | n2 | 52.017048 | 0.9998 | 2.1186 | sorting |  |
| insertion_sort | reverse_sorted | n2 | 135.531936 | 0.9998 | 2.2846 | sorting |  |
| insertion_sort | sorted | n | 9237.944785 | 0.9977 | 1.1378 | sorting |  |
| merge_sort | composite | n2 | 1.137172 | 0.9997 | 1.315 | sorting |  |
| merge_sort | integer_zone | n2 | 1.003205 | 0.9997 | 1.384 | sorting |  |
| merge_sort | many_duplicates | n2 | 0.985735 | 0.9998 | 1.4529 | sorting |  |
| merge_sort | nearly_sorted | n_log_n | 815.305266 | 0.9998 | 1.104 | sorting |  |
| merge_sort | random | n_log_n | 792.363416 | 0.9998 | 1.0867 | sorting |  |
| merge_sort | reverse_sorted | n_log_n | 774.177381 | 0.9995 | 1.0905 | sorting |  |
| merge_sort | sorted | n_log_n | 763.128182 | 0.9994 | 1.0539 | sorting |  |
| quick_sort | composite | n | 15052.824593 | 0.8825 | 0.6969 | sorting |  |
| quick_sort | integer_zone | n | 17177.583542 | -1.0944 | 0.6057 | sorting |  |
| quick_sort | many_duplicates | n | 25716.399361 | -1.5078 | 0.4412 | sorting |  |
| quick_sort | nearly_sorted | n | 13098.56329 | 0.8831 | 0.6169 | sorting |  |
| quick_sort | random | n | 14301.52529 | 0.2438 | 0.7598 | sorting |  |
| quick_sort | reverse_sorted | n | 13219.598018 | 0.8596 | 0.6498 | sorting |  |
| quick_sort | sorted | n | 13073.040838 | 0.8075 | 0.6214 | sorting |  |
| quick_sort_naive | composite | n_log_n | 840.307773 | 0.9985 | 1.0736 | sorting |  |
| quick_sort_naive | integer_zone | n2 | 5.337663 | 0.9967 | 1.5476 | sorting |  |
| quick_sort_naive | many_duplicates | n2 | 19.101927 | 0.9993 | 1.7516 | sorting |  |
| quick_sort_naive | nearly_sorted | n | 18203.901553 | 0.9305 | 0.7527 | sorting |  |
| quick_sort_naive | random | n | 9845.414739 | 0.9779 | 0.8686 | sorting |  |
| quick_sort_naive | reverse_sorted | n2 | 68.994047 | 0.9999 | 1.9037 | sorting |  |
| quick_sort_naive | sorted | n2 | 48.855934 | 0.9817 | 1.8602 | sorting |  |
| radix_sort | integer_zone | n_log_n | 506.031606 | 0.9994 | 1.0421 | sorting |  |
| radix_sort | many_duplicates | n | 7976.151039 | 0.9996 | 1.0588 | sorting |  |
| timsort | composite | n_log_n | 577.537877 | 0.9997 | 1.073 | sorting |  |
| timsort | integer_zone | n | 7530.128355 | 0.9998 | 1.0351 | sorting |  |
| timsort | many_duplicates | n | 7539.432565 | 0.9998 | 0.9909 | sorting |  |
| timsort | nearly_sorted | n_log_n | 498.712082 | 0.9995 | 1.0487 | sorting |  |
| timsort | random | n | 7133.935595 | 0.9999 | 1.0247 | sorting |  |
| timsort | reverse_sorted | n_log_n | 496.263753 | 0.9999 | 1.0265 | sorting |  |
| timsort | sorted | n | 7522.987254 | 0.9997 | 1.0433 | sorting |  |
| bellman_ford |  | VE | 44.055456 | 0.206 | 2.596 | graph | dense |
| bellman_ford |  | VE | 31.735673 | 0.2037 | 1.6413 | graph | sparse |
| dijkstra_array |  | V2 | 87.00781 | 0.9995 | 2.0968 | graph | dense |
| dijkstra_array |  | V2 | 53.489962 | 0.9994 | 2.0611 | graph | sparse |
| dijkstra_heap |  | V2 | 57.484987 | 0.995 | 2.2161 | graph | dense |
| dijkstra_heap |  | V_logV_E | 70.424454 | 0.9865 | 1.1888 | graph | sparse |
| spfa |  | VE | 31.3343 | 0.2012 | 2.4716 | graph | dense |
| spfa |  | VE | 26.438743 | 0.2128 | 1.3983 | graph | sparse |

