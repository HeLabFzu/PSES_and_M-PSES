import sys
sys.path.append("..")

from parallel_swapping_strategies.pses_layer_greedy import pses_layer_greedy
from parallel_swapping_strategies.pses_segment_greedy import pses_segment_greedy
from parallel_swapping_strategies.imbalanced_binary_tree_layer_greedy import imbalanced_layer_greedy
from parallel_swapping_strategies.imbalanced_binary_tree_segment_greedy import imbalanced_segment_greedy
from parallel_swapping_strategies.balanced_binary_tree import balanced_binary_tree
from parallel_swapping_strategies.random_data_generator import random_data_generator
import time

if __name__=="__main__":
    pses_layer_algorithm_time_cost = []
    imbalanced_layer_algorithm_time_cost = []
    pses_segment_algorithm_time_cost = []
    imbalanced_segment_algorithm_time_cost = []
    balanced_algorithm_time_cost = []

    for path_lenth in range(5,21):
        std = 75
        path, cost = random_data_generator(path_lenth, std)

        time_start = time.perf_counter()  
        pses_layer_final_solution, pses_layer_final_solution_costs_saving = pses_layer_greedy(path,cost,final_solution=[],final_solution_costs_saving=0)
        time_end = time.perf_counter()
        pses_layer_algorithm_time_cost.append((time_end - time_start)*1000)

        time_start = time.perf_counter()
        imbalanced_layer_final_solution, imbalanced_layer_final_solution_costs_saving = imbalanced_layer_greedy(path,cost,final_solution=[],final_solution_costs_saving=0)
        time_end = time.perf_counter()
        imbalanced_layer_algorithm_time_cost.append((time_end - time_start)*1000)

        time_start = time.perf_counter()
        pses_segment_final_solution, pses_segment_final_solution_costs_saving = pses_segment_greedy(path,cost)
        time_end = time.perf_counter()
        pses_segment_algorithm_time_cost.append((time_end - time_start)*1000)

        time_start = time.perf_counter()
        imbalanced_segment_final_solution, imbalanced_segment_final_solution_costs_saving = imbalanced_segment_greedy(path,cost)
        time_end = time.perf_counter()
        imbalanced_segment_algorithm_time_cost.append((time_end - time_start)*1000)

        time_start = time.perf_counter()
        balanced_final_solution, balanced_final_solution_costs_saving = balanced_binary_tree(path,cost)
        time_end = time.perf_counter()
        balanced_algorithm_time_cost.append((time_end - time_start)*1000)

    for i in range (0,len(pses_layer_algorithm_time_cost)):
        print("path_lenth is {} hops:" .format(i+5))
        print("pses_layer time cost is {} ms" .format(pses_layer_algorithm_time_cost[i]))
        print("imbalanced_layer time cost is {} ms" .format(imbalanced_layer_algorithm_time_cost[i]))
        print("pses_segment time cost is {} ms" .format(pses_segment_algorithm_time_cost[i]))
        print("imbalanced_segment time cost is {} ms" .format(imbalanced_segment_algorithm_time_cost[i]))
        print("balanced_binary_tree time cost is {} ms" .format(balanced_algorithm_time_cost[i]))
        print("--------------------------------------")
        
