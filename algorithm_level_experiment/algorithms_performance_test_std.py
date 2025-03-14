import sys
sys.path.append("..")

from parallel_swapping_strategies.pses_layer_greedy import pses_layer_greedy
from parallel_swapping_strategies.pses_segment_greedy import pses_segment_greedy
from parallel_swapping_strategies.imbalanced_binary_tree_layer_greedy import imbalanced_layer_greedy
from parallel_swapping_strategies.imbalanced_binary_tree_segment_greedy import imbalanced_segment_greedy
from parallel_swapping_strategies.balanced_binary_tree import balanced_binary_tree
from parallel_swapping_strategies.random_data_generator import random_data_generator

if __name__=="__main__":
    for std in [0,5,10,15,25,50]:
        path_lenth = 6
        pses_layer_total_saving_cost = 0
        imbalanced_layer_total_saving_cost = 0
        pses_segment_total_saving_cost = 0
        imbalanced_segment_total_saving_cost = 0
        balanced_total_saving_cost = 0

        for i in range(0,100):
            path, cost = random_data_generator(path_lenth, std)

            pses_layer_final_solution, pses_layer_final_solution_costs_saving = pses_layer_greedy(path,cost,final_solution=[],final_solution_costs_saving=0)
            pses_layer_total_saving_cost = pses_layer_total_saving_cost + pses_layer_final_solution_costs_saving

            imbalanced_layer_final_solution, imbalanced_layer_final_solution_costs_saving = imbalanced_layer_greedy(path,cost,final_solution=[],final_solution_costs_saving=0)
            imbalanced_layer_total_saving_cost = imbalanced_layer_total_saving_cost + imbalanced_layer_final_solution_costs_saving

            pses_segment_final_solution, pses_segment_final_solution_costs_saving = pses_segment_greedy(path,cost)
            pses_segment_total_saving_cost = pses_segment_total_saving_cost + pses_segment_final_solution_costs_saving

            imbalanced_segment_final_solution, imbalanced_segment_final_solution_costs_saving = imbalanced_segment_greedy(path,cost)
            imbalanced_segment_total_saving_cost = imbalanced_segment_total_saving_cost + imbalanced_segment_final_solution_costs_saving

            balanced_final_solution, balanced_final_solution_costs_saving = balanced_binary_tree(path,cost)
            balanced_total_saving_cost = balanced_total_saving_cost + balanced_final_solution_costs_saving

        print("std is {}" .format(std))
        print("path_lenth is {} hops" .format(path_lenth))
        print("pses_layer saving cost is: {}" .format(pses_layer_total_saving_cost/100))
        print("imbalanced_layer saving cost is: {}" .format(imbalanced_layer_total_saving_cost/100))
        print("pses_segment saving cost is: {}" .format(pses_segment_total_saving_cost/100))
        print("imbalanced_segment saving cost is: {}" .format(imbalanced_segment_total_saving_cost/100))
        print("balanced_binary_tree saving cost is: {}" .format(balanced_total_saving_cost/100))
        print("--------------------------------------")
