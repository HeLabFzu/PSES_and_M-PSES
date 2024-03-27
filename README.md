# Repo for Parallel Segment Entanglement Swapping
## Abstract
Entanglement swapping in quantum networks is one way to obtain long-distance entanglement pairs, important resources for distributed quantum computing. In the noisy intermediate-scale quantum era, scientists are trying to improve the swapping success rate by researching anti-noise technology on the physical level, thus obtaining a higher generation rate of long-distance entanglement. However, we may improve the generation rate from another perspective, which is studying an efficient swapping strategy. This paper analyzes the challenges faced by existing swapping strategies, including the node allocation principle, time synchronization, and processing of swapping failure. We present Parallel Segment Entanglement Swapping (PSES) to solve these problems. The core idea of PSES is to segment the path and perform parallel swapping between segments to improve the generation rate of long-distance entanglement. We construct a tree-like model as the carrier of PSES and propose heuristic algorithms called Layer Greedy and Segment Greedy to transform the path into a tree-like model. Moreover, we realize the time synchronization and design the on-demand retransmission mechanism to process swapping failure. The experiments show that PSES performs superiorly to other swapping strategies, and the on-demand retransmission mechanism can reduce the average swapping time by 80% and the average entanglement consumption by 80%.
## Repository Structure
- `parallel_swapping_strategies`      source code of swapping strategies
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
	+ `parallel_swapping_simulation_performance_test.py`    avg swapping time vs. hops; avg swapping time vs. std of node costs
	+ `PSES_fail_node_on_demand_retransmission_test.py`     on-demand retransmission mechanism test
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