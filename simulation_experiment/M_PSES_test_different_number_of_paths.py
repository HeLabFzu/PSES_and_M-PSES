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
from multiprocessing.dummy import Pool as ThreadPool

name = globals()
def define_network(depolar_rates,dephase_rates,qchannel_loss_init,qchannel_loss_noisy,path_nodes_number):
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
    path_nodes_number = 6
#### avg 1.47, std 0.46 #####
    depolar_rates = [0,0.09,0.06,0.31,0.1,0]
    dephase_rates = [0,0.09,0.06,0.31,0.1,0]
    qchannel_loss_init = [0,0.01,0.01,0.02,0.006,0.2,0.01,0.012,0.04,0]
    qchannel_loss_noisy = [0,0.001,0.001,0.002,0.0006,0.02,0.001,0.012,0.004,0]   

###########################################################################################################################################################
   
###################################################### initialization ######################################################
    network_1,real_path_1 = define_network(depolar_rates,dephase_rates,qchannel_loss_init,qchannel_loss_noisy,path_nodes_number)
    central_controller = CentralController(network_1)
    path_1 = []
    for i in range(0,path_nodes_number):
        path_1.append("x"+str(i))
    ### call central_controller to caculate nodes' cost ###
    cost_1 = central_controller.nodes_cost_caculator(depolar_rates,dephase_rates,qchannel_loss_init,qchannel_loss_noisy)
    network_2,real_path_2 = define_network(depolar_rates,dephase_rates,qchannel_loss_init,qchannel_loss_noisy,path_nodes_number)

    network_2,real_path_2 = define_network(depolar_rates,dephase_rates,qchannel_loss_init,qchannel_loss_noisy,path_nodes_number)
    path_2 = []
    for i in range(0,path_nodes_number):
        path_2.append("x"+str(i))
    ### call central_controller to caculate nodes' cost ###
    cost_2 = central_controller.nodes_cost_caculator(depolar_rates,dephase_rates,qchannel_loss_init,qchannel_loss_noisy)

    network_3,real_path_3 = define_network(depolar_rates,dephase_rates,qchannel_loss_init,qchannel_loss_noisy,path_nodes_number)
    path_3 = []
    for i in range(0,path_nodes_number):
        path_3.append("x"+str(i))
    ### call central_controller to caculate nodes' cost ###
    cost_3 = central_controller.nodes_cost_caculator(depolar_rates,dephase_rates,qchannel_loss_init,qchannel_loss_noisy)

    network_4,real_path_4 = define_network(depolar_rates,dephase_rates,qchannel_loss_init,qchannel_loss_noisy,path_nodes_number)
    path_4 = []
    for i in range(0,path_nodes_number):
        path_4.append("x"+str(i))
    ### call central_controller to caculate nodes' cost ###
    cost_4 = central_controller.nodes_cost_caculator(depolar_rates,dephase_rates,qchannel_loss_init,qchannel_loss_noisy)

    network_5,real_path_5 = define_network(depolar_rates,dephase_rates,qchannel_loss_init,qchannel_loss_noisy,path_nodes_number)
    path_5 = []
    for i in range(0,path_nodes_number):
        path_5.append("x"+str(i))
    ### call central_controller to caculate nodes' cost ###
    cost_5 = central_controller.nodes_cost_caculator(depolar_rates,dephase_rates,qchannel_loss_init,qchannel_loss_noisy)

    network_6,real_path_6 = define_network(depolar_rates,dephase_rates,qchannel_loss_init,qchannel_loss_noisy,path_nodes_number)
    path_6 = []
    for i in range(0,path_nodes_number):
        path_6.append("x"+str(i))
    ### call central_controller to caculate nodes' cost ###
    cost_6 = central_controller.nodes_cost_caculator(depolar_rates,dephase_rates,qchannel_loss_init,qchannel_loss_noisy)


    pses_layer_final_solution_1, pses_layer_final_solution_costs_saving_1 = pses_layer_greedy(path_1,cost_1,final_solution=[],final_solution_costs_saving=0)
    pses_layer_final_solution_2, pses_layer_final_solution_costs_saving_2 = pses_layer_greedy(path_2,cost_2,final_solution=[],final_solution_costs_saving=0)
    pses_layer_final_solution_3, pses_layer_final_solution_costs_saving_3 = pses_layer_greedy(path_3,cost_3,final_solution=[],final_solution_costs_saving=0)
    pses_layer_final_solution_4, pses_layer_final_solution_costs_saving_4 = pses_layer_greedy(path_4,cost_4,final_solution=[],final_solution_costs_saving=0)
    pses_layer_final_solution_5, pses_layer_final_solution_costs_saving_5 = pses_layer_greedy(path_5,cost_5,final_solution=[],final_solution_costs_saving=0)
    pses_layer_final_solution_6, pses_layer_final_solution_costs_saving_6 = pses_layer_greedy(path_6,cost_6,final_solution=[],final_solution_costs_saving=0)
    entangle_distribution_protocols_1, entangle_swapping_protocols_1 = define_protocol(pses_layer_final_solution_1,real_path_1)
    entangle_distribution_protocols_2, entangle_swapping_protocols_2 = define_protocol(pses_layer_final_solution_2,real_path_2)
    entangle_distribution_protocols_3, entangle_swapping_protocols_3 = define_protocol(pses_layer_final_solution_3,real_path_3)
    entangle_distribution_protocols_4, entangle_swapping_protocols_4 = define_protocol(pses_layer_final_solution_4,real_path_4)
    entangle_distribution_protocols_5, entangle_swapping_protocols_5 = define_protocol(pses_layer_final_solution_5,real_path_5)
    entangle_distribution_protocols_6, entangle_swapping_protocols_6 = define_protocol(pses_layer_final_solution_6,real_path_6)
##############################################################################################################################

########################## pses test (2~6 paths) ###########################
#    time_start = time.perf_counter()
#    central_controller.parallel_swapping(pses_layer_final_solution_1, entangle_distribution_protocols_1, entangle_swapping_protocols_1, network_1, False)
#    central_controller.parallel_swapping(pses_layer_final_solution_2, entangle_distribution_protocols_2, entangle_swapping_protocols_2, network_2, False)
#    central_controller.parallel_swapping(pses_layer_final_solution_3, entangle_distribution_protocols_3, entangle_swapping_protocols_3, network_3, False)
#    central_controller.parallel_swapping(pses_layer_final_solution_4, entangle_distribution_protocols_4, entangle_swapping_protocols_4, network_4, False)
#    central_controller.parallel_swapping(pses_layer_final_solution_5, entangle_distribution_protocols_5, entangle_swapping_protocols_5, network_5, False)
#    central_controller.parallel_swapping(pses_layer_final_solution_6, entangle_distribution_protocols_6, entangle_swapping_protocols_6, network_6, False)
#    time_stop = time.perf_counter()
#    pses_time = time_stop-time_start
#    print("pses time is: {}" .format(pses_time))
########################## M-PSES test (2~6 paths)###########################
    solution_set = []
    entangle_distribution_protocols_set = []
    entangle_swapping_protocols_set = []
    network_set = []
    solution_set.append(pses_layer_final_solution_1)
    solution_set.append(pses_layer_final_solution_2)
#    solution_set.append(pses_layer_final_solution_3)
#    solution_set.append(pses_layer_final_solution_4)
#    solution_set.append(pses_layer_final_solution_5)
#    solution_set.append(pses_layer_final_solution_6)
    entangle_distribution_protocols_set.append(entangle_distribution_protocols_1)
    entangle_distribution_protocols_set.append(entangle_distribution_protocols_2)
#    entangle_distribution_protocols_set.append(entangle_distribution_protocols_3)
#    entangle_distribution_protocols_set.append(entangle_distribution_protocols_4)
#    entangle_distribution_protocols_set.append(entangle_distribution_protocols_5)
#    entangle_distribution_protocols_set.append(entangle_distribution_protocols_6)
    entangle_swapping_protocols_set.append(entangle_swapping_protocols_1)
    entangle_swapping_protocols_set.append(entangle_swapping_protocols_2)
#    entangle_swapping_protocols_set.append(entangle_swapping_protocols_3)
#    entangle_swapping_protocols_set.append(entangle_swapping_protocols_4)
#    entangle_swapping_protocols_set.append(entangle_swapping_protocols_5)
#    entangle_swapping_protocols_set.append(entangle_swapping_protocols_6)
    network_set.append(network_1)
    network_set.append(network_2)
#    network_set.append(network_3)
#    network_set.append(network_4)
#    network_set.append(network_5)
#    network_set.append(network_6)
    common_node_list = ['x3']
    time_start = time.perf_counter()
    ### call central_controller to exec solution (parallel swapping) ###
    central_controller.MPSES_parallel_swapping(solution_set, entangle_distribution_protocols_set, entangle_swapping_protocols_set, network_set, False, common_node_list)
    time_stop = time.perf_counter()
    mpses_time = time_stop-time_start
    print("mpses time is: {}" .format(mpses_time))
##############################################################################
