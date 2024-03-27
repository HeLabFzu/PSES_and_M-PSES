import math
import copy

def pses_find_layer_solutions(path,cost):
    layer_solutions = []
    temp_a = []  # curren layer solutions which's number of segments is sn
    segment = []
    ### sn means the number of segments in a path. ###
    sn = 2
    max_sn = math.ceil((len(path)-2)/2)

    ### case: sn=1 ###
    for i in range(1,len(path)-1):
        segment = [path[i-1],path[i],path[i+1]]
        solution = [segment]
        layer_solutions.append(solution)
        temp_a.append(solution)
        for j in range (i+2, len(path)):
              segment = copy.deepcopy(segment)
              segment.append(path[j])
              solution = [segment]
              layer_solutions.append(solution)
              temp_a.append(solution)

    ### case: sn>1 ###
    while sn<=max_sn:
        temp_b = []

        for solution in temp_a:
            i = path.index(solution[-1][-2])
            for j in range(i+2,len(path)-1):
                segment=[path[j-1],path[j],path[j+1]]
                solution_temp = copy.deepcopy(solution)
                solution_temp.append(segment)
                layer_solutions.append(solution_temp)
                temp_b.append(solution_temp)
                for k in range(j+2, len(path)):
                    segment = copy.deepcopy(segment)
                    segment.append(path[k])
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
            segment_cost = 0
            for node in segment[1:-1]:
                left_path.remove(node)
                segment_cost = segment_cost + cost[node]
            total_cost = total_cost + segment_cost
            if segment_cost > max_cost:
                max_cost = segment_cost
        layer_solutions_costs_saving.append(total_cost-max_cost)
        layer_solutions_left_paths.append(left_path)
    return layer_solutions,layer_solutions_left_paths,layer_solutions_costs_saving

def pses_layer_greedy(path,cost,final_solution,final_solution_costs_saving):
    while len(path) > 2:
        layer_solutions,layer_solutions_left_paths,layer_solutions_costs_saving = pses_find_layer_solutions(path,cost)
        best_layer_solution_id = layer_solutions_costs_saving.index(max(layer_solutions_costs_saving))
        final_solution.append(layer_solutions[best_layer_solution_id])
        final_solution_costs_saving = final_solution_costs_saving + layer_solutions_costs_saving[best_layer_solution_id]
        path = layer_solutions_left_paths[best_layer_solution_id]
        return pses_layer_greedy(path,cost,final_solution,final_solution_costs_saving)
    return final_solution, final_solution_costs_saving

if __name__=="__main__":
    path=["x0","x1","x2","x3","x4","x5"]
    cost = {'x0':0,'x1':50,'x2':49,'x3':20,'x4':100,'x5':0}
    final_solution, final_solution_costs_saving = pses_layer_greedy(path,cost,final_solution=[],final_solution_costs_saving=0)
    print("final solution is shown below:")
    for i in range(0,len(final_solution)):
        print("    layer {} is: {}" .format(i+1,final_solution[i]))
    print("total saving cost is: {}" .format(final_solution_costs_saving))
        
