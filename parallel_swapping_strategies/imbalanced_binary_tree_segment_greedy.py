import copy
import math
def imbalanced_segment_greedy(path,cost):
    cost = list(cost.values())
    final_solution = []
    final_solution_costs_saving = 0

    ### find final solution by Greedy###
    while len(path)-2>0:
        solution = []
        left_path = copy.deepcopy(path)
        left_nodes_cost = copy.deepcopy(cost)
        max_segment_cost = 0

        ### first segment ###
        segment = [path[0],path[1],path[2]]
        solution.append(segment)
        left_nodes_cost.pop(1)
        left_path.pop(1)
        max_segment_cost = cost[1]

        ### other segments ###
        i = 3
        while i in range(3,len(path)-1):

                ### if net benefit >= 0 add segment, or do not add segment ###
                if min(cost[i], max_segment_cost) - max(0,cost[i]-max_segment_cost) < 0:
                    i = i + 1
                else: 
                    segment = [path[i-1],path[i],path[i+1]]
                    solution.append(segment)
                    left_nodes_cost.pop(left_path.index(path[i]))
                    left_path.remove(path[i])
                    if cost[i] > max_segment_cost:
                        final_solution_costs_saving = final_solution_costs_saving + max_segment_cost
                        max_segment_cost = cost[i]
                    else:
                        final_solution_costs_saving = final_solution_costs_saving + cost[i]
                    i = i + 2

        ### add layer solution to final solution ###
        final_solution.append(solution)
        ### reorganize path and cost ###
        path = copy.deepcopy(left_path)
        cost = copy.deepcopy(left_nodes_cost)
                 
    return final_solution, final_solution_costs_saving

        
if __name__=="__main__":
    path=["x0","x1","x2","x3","x4","x5"]
    cost = {'x0':0,'x1':50,'x2':49,'x3':20,'x4':100,'x5':0}
    final_solution, final_solution_costs_saving = imbalanced_segment_greedy(path,cost)
    print("final solution is shown below:")
    for i in range(0,len(final_solution)):
        print("    layer {} is: {}" .format(i+1,final_solution[i]))
    print("total saving cost is: {}" .format(final_solution_costs_saving))

