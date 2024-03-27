import math
import copy

def imbalanced_find_layer_solutions(path,cost):
    layer_solutions = []
    temp_a = []
    segment = []
    ### sn means the number of segments in a path. ###
    sn = 2
    max_sn = math.ceil((len(path)-2)/2)

    ### case: sn=1 ###
    for i in range(1,len(path)-1):
        segment=[path[i-1],path[i],path[i+1]]
        solution=[segment]
        layer_solutions.append(solution)
        temp_a.append(solution)

    ### case: sn>1 ###
    while sn<=max_sn:
        temp_b = []
        for solution in temp_a:
            i = path.index(solution[len(solution)-1][1])
            for j in range(i+2,len(path)-1):
                segment=[path[j-1],path[j],path[j+1]]
                solution_temp = copy.deepcopy(solution)
                solution_temp.append(segment)
                layer_solutions.append(solution_temp)
                temp_b.append(solution_temp)
        temp_a = copy.deepcopy(temp_b)
        sn=sn+1

    layer_solutions_costs_saving = []
    layer_solutions_left_paths = []
    for solution in layer_solutions:
        left_path = copy.deepcopy(path)
        max_cost = 0
        total_cost = 0
        for segment in solution:
            left_path.remove(segment[1])
            segment_cost = cost[segment[1]]
            total_cost = total_cost + segment_cost
            if segment_cost > max_cost:
                max_cost = segment_cost
        layer_solutions_costs_saving.append(total_cost-max_cost)
        layer_solutions_left_paths.append(left_path)
    return layer_solutions,layer_solutions_left_paths,layer_solutions_costs_saving

def imbalanced_layer_greedy(path,cost,final_solution,final_solution_costs_saving):
    while len(path) > 2:
        layer_solutions,layer_solutions_left_paths,layer_solutions_costs_saving = imbalanced_find_layer_solutions(path,cost)
        final_solution.append(layer_solutions[layer_solutions_costs_saving.index(max(layer_solutions_costs_saving))])
        final_solution_costs_saving = final_solution_costs_saving + max(layer_solutions_costs_saving)
        path = layer_solutions_left_paths[layer_solutions_costs_saving.index(max(layer_solutions_costs_saving))]
        return imbalanced_layer_greedy(path,cost,final_solution,final_solution_costs_saving)
    return final_solution, final_solution_costs_saving

if __name__=="__main__":
    path=["x0","x1","x2","x3","x4","x5"]
    cost = {'x0':0,'x1':50,'x2':49,'x3':20,'x4':100,'x5':0}
    final_solution, final_solution_costs_saving = imbalanced_layer_greedy(path,cost,final_solution=[],final_solution_costs_saving=0)
    print("final solution is shown below:")
    for i in range(0,len(final_solution)):
        print("    layer {} is: {}" .format(i+1,final_solution[i]))
    print("total saving cost is: {}" .format(final_solution_costs_saving))


