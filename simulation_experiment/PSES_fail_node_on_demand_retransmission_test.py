import sys
sys.path.append("..")

import netsquid as ns
import pandas
import pydynaa
import time
import numpy as np
from topology.Centralized_Chain_Path import Centralized_Cellular_Chain_Path_setup
from protocol.centralized.CentralizedEntanglementDistribution import CentralizedEntanglementDistribution
from protocol.centralized.CentralizedSwapping import CentralizedSwapping
from protocol.centralized.CentralizedTeleportation import CentralizedTeleportation
from util.CheckDistribution import CheckDistribution
from util.NodeStruct import NodeStruct
from util.CentralController import CentralController
from parallel_swapping_strategies.pses_layer_greedy import pses_layer_greedy
from parallel_swapping_strategies.pses_segment_greedy import pses_segment_greedy
from parallel_swapping_strategies.imbalanced_binary_tree_layer_greedy import imbalanced_layer_greedy
from parallel_swapping_strategies.imbalanced_binary_tree_segment_greedy import imbalanced_segment_greedy
from parallel_swapping_strategies.balanced_binary_tree import balanced_binary_tree


def define_network(depolar_rates,dephase_rates,qchannel_loss_init,qchannel_loss_noisy,path_nodes_number):
    name = globals()
    network = Centralized_Cellular_Chain_Path_setup(depolar_rates=depolar_rates,dephase_rates=dephase_rates,qchannel_loss_init=qchannel_loss_init,qchannel_loss_noisy=qchannel_loss_noisy, hops=path_nodes_number)
    Central_Controller = network.subcomponents["Central_Controller"]
    for i in range(0,path_nodes_number):
        name['x'+str(i)] = network.subcomponents['x'+str(i)]
        if i != path_nodes_number-1:
            name['c'+str(i)] = network.subcomponents['c'+str(i)]

    path = []
    for i in range(0,path_nodes_number):
        if i == 0:
            path.append(NodeStruct(node=name['x'+str(i)],entangle_distribution_role="user",
                              store_mem_pos_1=1))
            path.append(NodeStruct(node=name['c'+str(i)],entangle_distribution_role="controller",
                              qsource_name="c" + str(i) + "_" + "x" + str(i) + "_" + "x" + str(i+1)+ "_" + "QSource"))
        elif i == path_nodes_number-1:
            path.append(NodeStruct(node=name['x'+str(i)],entangle_distribution_role="user",
                              store_mem_pos_1=1))
        else:
            path.append(NodeStruct(node=name['x'+str(i)],entangle_distribution_role="repeater",
                             store_mem_pos_1=1,store_mem_pos_2=2))
            path.append(NodeStruct(node=name['c'+str(i)],entangle_distribution_role="controller",
                             qsource_name="c" + str(i) + "_" + "x" + str(i) + "_" + "x" + str(i+1)+ "_" + "QSource"))

    return network,path

def define_protocol(final_solution,path):
    ### define distribution protocols ###
    entangle_distribution_protocols = []
    for layer_solution in final_solution:
        entangle_distribution_protocols_layer = []
        for segment in layer_solution:
            entangle_distribution_protocols_segment = []
            for i in range(0,len(segment)-1):
                entangle_distribution_protocol_temp = []
                if int(segment[i][1:])+1 == int(segment[i+1][1:]):
                    if int(segment[i][1:]) == 0:
                        entangle_distribution_protocol_temp.append(CentralizedEntanglementDistribution(node=path[int(segment[i][1:])*2].node,
                                                                                   role=path[int(segment[i][1:])*2].entangle_distribution_role,
                                                                                   store_mem_pos=path[int(segment[i][1:])*2].store_mem_pos_1))
                    else:
                        entangle_distribution_protocol_temp.append(CentralizedEntanglementDistribution(node=path[int(segment[i][1:])*2].node,
                                                                                   role=path[int(segment[i][1:])*2].entangle_distribution_role,
                                                                                   store_mem_pos=path[int(segment[i][1:])*2].store_mem_pos_2))

                    entangle_distribution_protocol_temp.append(CentralizedEntanglementDistribution(node=path[int(segment[i][1:])*2+1].node,
                                                                               role=path[int(segment[i][1:])*2+1].entangle_distribution_role,
                                                                               qsource_name=path[int(segment[i][1:])*2+1].qsource_name))

                    entangle_distribution_protocol_temp.append(CentralizedEntanglementDistribution(node=path[int(segment[i][1:])*2+2].node,
                                                                               role=path[int(segment[i][1:])*2+2].entangle_distribution_role,
                                                                               store_mem_pos=path[int(segment[i][1:])*2].store_mem_pos_1))
                    entangle_distribution_protocols_segment.append(entangle_distribution_protocol_temp)

            entangle_distribution_protocols_layer.append(entangle_distribution_protocols_segment) 

        entangle_distribution_protocols.append(entangle_distribution_protocols_layer)

    ### define swapping protocols ###
    entangle_swapping_protocols = []
    for layer_solution in final_solution:
        entangle_swapping_protocols_layer = []
        for segment in layer_solution:
            entangle_swapping_protocols_segment = []
            for i in range(1,len(segment)-1):
                entangle_swapping_protocol_temp = []
                entangle_swapping_protocol_temp.append(CentralizedSwapping(node=path[int(segment[i][1:])*2].node,
                                                  port=path[int(segment[i][1:])*2].node.get_conn_port(path[int(segment[i][1:])*2+1].node.ID),
                                                  role="repeater", repeater_mem_posA=path[int(segment[i][1:])*2].store_mem_pos_1,
                                                  repeater_mem_posB=path[int(segment[i][1:])*2].store_mem_pos_2))
                for j in range(1,int(segment[i+1][1:])*2 - int(segment[i][1:])*2):
                    entangle_swapping_protocol_temp.append(CentralizedSwapping(node=path[int(segment[i][1:])*2+j].node,
                                                  port=path[int(segment[i][1:])*2+j].node.get_conn_port(path[int(segment[i][1:])*2+j-1].node.ID),
                                                  portout=path[int(segment[i][1:])*2+j].node.get_conn_port(path[int(segment[i][1:])*2+j+1].node.ID),
                                                  role="localcontroller"))
                entangle_swapping_protocol_temp.append(CentralizedSwapping(node=path[int(segment[i+1][1:])*2].node,
                                                  port=path[int(segment[i+1][1:])*2].node.get_conn_port(path[int(segment[i+1][1:])*2-1].node.ID),
                                                  role="corrector", corrector_mem_pos=path[int(segment[i+1][1:])*2].store_mem_pos_1))
                entangle_swapping_protocols_segment.append(entangle_swapping_protocol_temp)
            entangle_swapping_protocols_layer.append(entangle_swapping_protocols_segment)
        entangle_swapping_protocols.append(entangle_swapping_protocols_layer) 

    return entangle_distribution_protocols, entangle_swapping_protocols

if __name__ == '__main__':
##################################### test data ##############################################
    path_nodes_number = 5
######## avg 1.44, std 0.13 #########
    depolar_rates = [0,0.1,0.15,0.2,0]
    dephase_rates = [0,0.1,0.15,0.2,0]
    qchannel_loss_init = [0,0.018,0.018,0.015,0.015,0.02,0.02,0]
    qchannel_loss_noisy = [0,0.0018,0.0018,0.0015,0.0015,0.002,0.002,0]
##############################################################################################
 
########################### Failed Node On-Demand Repreparation test ########################### 
    network,real_path = define_network(depolar_rates,dephase_rates,qchannel_loss_init,qchannel_loss_noisy,path_nodes_number)
    central_controller = CentralController(network)

    path = []
    for i in range(0,path_nodes_number):
        path.append("x"+str(i))
    ### call central_controller to caculate nodes' cost ###
    cost = central_controller.nodes_cost_caculator(depolar_rates,dephase_rates,qchannel_loss_init,qchannel_loss_noisy)
    cost_array = list(cost.values())
    cost_array.pop(0)
    cost_array.pop(-1)
    cost_std = np.std(cost_array)
    cost_average = np.average(cost_array)
    pses_layer_final_solution, pses_layer_final_solution_costs_saving = pses_layer_greedy(path,cost,final_solution=[],final_solution_costs_saving=0)
    entangle_distribution_protocols, entangle_swapping_protocols = define_protocol(pses_layer_final_solution,real_path)
    time_start = time.perf_counter()
    ### central_controller.parallel_swapping_on_demand_policy includes Failed Node On-Demand Repreparation Control. Call central_controller to exec solution (parallel swapping).###
    central_controller.parallel_swapping_on_demand_policy(pses_layer_final_solution, entangle_distribution_protocols, entangle_swapping_protocols, network, False)
    time_stop = time.perf_counter()
    pses_layer_time = time_stop-time_start
    print("cost std is: {}" .format(cost_std))
    print("cost average is: {}" .format(cost_average))
    print("entanglement swapping time is: {}" .format(pses_layer_time))
    print("the number of consumed entangled pairs is: {}". format(central_controller.get_number_of_entangled_pairs()))
###############################################################################

########################### Full Path Repreparation test ###########################
#    total_time = 0
#    total_pairs = 0
#    while True:   
#        network,real_path = define_network(depolar_rates,dephase_rates,qchannel_loss_init,qchannel_loss_noisy,path_nodes_number)
#        central_controller = CentralController(network)
#        path = []
#        for i in range(0,path_nodes_number):
#            path.append("x"+str(i))
#        ### call central_controller to caculate nodes' cost ###
#        cost = central_controller.nodes_cost_caculator(depolar_rates,dephase_rates,qchannel_loss_init,qchannel_loss_noisy)
#        cost_array = list(cost.values())
#        cost_array.pop(0)
#        cost_array.pop(-1)
#        cost_std = np.std(cost_array)
#        cost_average = np.average(cost_array)
#        pses_layer_final_solution, pses_layer_final_solution_costs_saving = pses_layer_greedy(path,cost,final_solution=[],final_solution_costs_saving=0)
#        entangle_distribution_protocols, entangle_swapping_protocols = define_protocol(pses_layer_final_solution,real_path)
#
#        ### central_controller.parallel_swapping_full_path_policy includes Full Path Repreparation Control. Call central_controller to exec solution (parallel swapping).###
#        time_start = time.perf_counter()   
#        central_controller.parallel_swapping_full_path_policy(pses_layer_final_solution, entangle_distribution_protocols, entangle_swapping_protocols, network, False)
#        time_stop = time.perf_counter()
#        total_time = total_time + time_stop - time_start
#        total_pairs = total_pairs + central_controller.get_number_of_entangled_pairs()
#        if central_controller.get_is_failed_node() == False:
#            break
#        ### timesleep, to avoid protocol block error, does not count as entanglement swapping time ###
#        time.sleep(1)
#    print("cost std is: {}" .format(cost_std))
#    print("cost average is: {}" .format(cost_average))
#    print("entanglement swapping time is: {}" .format(total_time))
#    print("the number of consumed entangled pairs is: {}". format(total_pairs))
###############################################################################
