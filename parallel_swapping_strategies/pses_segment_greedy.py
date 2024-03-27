import copy
import math
def pses_segment_greedy(path,cost):
    cost = list(cost.values())
    final_solution = []
    final_solution_costs_saving = 0

    ### find final solution by Greedy###
    while len(path)-2>0:
        solution = []
        left_path = copy.deepcopy(path)
        left_nodes_cost = copy.deepcopy(cost)
        max_segment_cost = 0

        ### first segment###
        segment = [path[0],path[1],path[2]]
        solution.append(segment)
        left_nodes_cost.pop(1)
        left_path.pop(1)
        max_segment_cost = cost[1]

        ### other segments ###
        i = 3
        segment = []
        while i in range(3,len(path)-1):
           
            ### a new segment ###
            if len(segment) == 0:  
 
                ### if net benefit >= 0 add a new segment, or do not add segment ###
                current_segment_net_benefit = min(cost[i], max_segment_cost) - max(0, cost[i] - max_segment_cost)
                if current_segment_net_benefit < 0:
                    i = i + 1
                else:
                    segment = [path[i-1],path[i],path[i+1]]
                    left_nodes_cost.pop(left_path.index(path[i]))
                    left_path.remove(path[i])
                    current_segment_cost = cost[i]
                    i = i + 1
                    if i == len(path)-1:
                        solution.append(segment)
                        if current_segment_cost > max_segment_cost:
                            final_solution_costs_saving = final_solution_costs_saving + max_segment_cost
                        else:
                            final_solution_costs_saving = final_solution_costs_saving + current_segment_cost

            ### add a node to last segment to form a composite segment###
            else:
                future_segment_net_benefit = min(current_segment_cost + cost[i], max_segment_cost) - max(0, current_segment_cost + cost[i] - max_segment_cost)

                ### if the segment_net_benefit decrease after a node is added, then do not add the node. otherwise, add the node to form a composite segment ### 
                if future_segment_net_benefit < current_segment_net_benefit: 
                    solution.append(segment)
                    if current_segment_cost > max_segment_cost:
                        final_solution_costs_saving = final_solution_costs_saving + max_segment_cost
                        max_segment_cost = current_segment_cost
                    else:
                        final_solution_costs_saving = final_solution_costs_saving + current_segment_cost
                    segment = []
                    i = i + 1
                else:
                    segment.append(path[i+1])
                    left_nodes_cost.pop(left_path.index(path[i]))
                    left_path.remove(path[i])
                    current_segment_cost = current_segment_cost + cost[i]
                    current_segment_net_benefit = future_segment_net_benefit
                    i = i + 1
                    if i == len(path)-1:
                        solution.append(segment)
                        if current_segment_cost > max_segment_cost:
                            final_solution_costs_saving = final_solution_costs_saving + max_segment_cost
                        else:
                            final_solution_costs_saving = final_solution_costs_saving + current_segment_cost

        ### add layer solution to final solution ###
        final_solution.append(solution)
        ### reorganize path and cost ###
        path = copy.deepcopy(left_path)
        cost = copy.deepcopy(left_nodes_cost)

    return final_solution, final_solution_costs_saving


#if __name__=="__main__":
#    path=["x0","x1","x2","x3","x4","x5","x6","x7","x8","x9","x10","x11","x12","x13","x14"]
#    cost = {'x0':0,'x1':100,'x2':1,'x3':100,'x4':1,'x5':100,'x6':1,'x7':100,'x8':1,'x9':100,'x10':1,'x11':1,'x12':1,'x13':100,'x14':0}
#    final_solution, final_solution_costs_saving = pses_segment_greedy(path,cost)
#    print("final solution is shown below:")
#    for i in range(0,len(final_solution)):
#        print("    layer {} is: {}" .format(i+1,final_solution[i]))
#    print("total saving cost is: {}" .format(final_solution_costs_saving))
