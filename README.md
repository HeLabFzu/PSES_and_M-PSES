# Repo for PSES and M-PSES
## Repository Structure
- `parallel_swapping_strategies`      source code of parallel ES strategies
	+ `balanced_binary_tree.py`    Balanced Binary Tree (BBT) strategy
	+ `imbalanced_binary_tree_layer_greedy.py` Imbalanced Binary Tree (IBT) strategy with Layer Greedy
	+ `imbalanced_binary_tree_segment_greedy.py`  Imbalanced Binary Tree (IBT) strategy with Segment Greedy
	+ `pses_layer_greedy.py` Parallel Segment Entanglement Swapping (PSES) strategy with Layer Greedy
	+ `pses_segment_greedy.py` Parallel Segment Entanglement Swapping (PSES) strategy with Segment Greedy
	+ `random_data_generator` quantified node cost random data generator with a Gaussian distribution for algorithm-level experiment
- `algorithm_level_experiment`      source code of algorithm-level experiments
	+ `algorithms_performance_test_hops.py`    performance vs. hops
	+ `algorithms_performance_test_std.py`     performance vs. std of node costs
	+ `algorithms_performance_test_time.py`    time complexity
- `simulation_experiment`      source code of simulation experiments
	+ `parallel_swapping_simulation_performance_test.py`    avg ES time vs. hops; avg ES time vs. std of node costs
	+ `PSES_fail_node_on_demand_retransmission_test.py`     on-demand retransmission mechanism test
	+ `M_PSES_test_different_number_of_common_nodes.py`       effectiveness of M-PSES vs. number of common nodes
	+ `M_PSES_test_different_number_of_paths.py`          Effectiveness of M-PSES vs. number of paths
- `protocol`     dependency files; protocols for hierarchical quantum network
- `topology`     dependency files; topologies for hierarchical quantum network
- `util`         dependency files; utilities functions for hierarchical quantum network

## Run Experiments
```bash
# 1. *This step is platform-specific* 
# install Python >= 3.8.2, NetSquid >= 1.1.5 (prefer to install NetSquid 1.1.5)
# 2. Install NetSquid
# refer to https://docs.netsquid.org/latest-release/INSTALL.html
# NetSquid might require additional python package, please refer to the UserBook of NetSquid
# 3. Download source code
# git clone https://github.com/hebinjie33/PSES.git
# 4. Run test
# python3 xxx.py
```
## Authors
- Binjie He (hebinjie33@gmail.com)