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
    path_nodes_number = 6
######## avg 1.44, std 0.13 #########
    depolar_rates = [0,0.1,0.15,0.2,0.18,0]
    dephase_rates = [0,0.1,0.15,0.2,0.18,0]
    qchannel_loss_init = [0,0.018,0.018,0.015,0.015,0.02,0.02,0.018,0.018,0]
    qchannel_loss_noisy = [0,0.0018,0.0018,0.0015,0.0015,0.002,0.002,0.0018,0.0018,0]


########  avg 1.46, std 0.21 #########
#    depolar_rates = [0,0.1,0.15,0.25,0.15,0]
#    dephase_rates = [0,0.1,0.15,0.25,0.15,0]
#    qchannel_loss_init = [0,0.018,0.018,0.015,0.015,0.025,0.025,0.015,0.015,0]
#    qchannel_loss_noisy = [0,0.0018,0.0018,0.0015,0.0025,0.0025,0.003,0.0015,0.0015,0]

########  avg 1.47, std 0.35 #########
#    depolar_rates = [0,0.08,0.12,0.3,0.12,0]
#    dephase_rates = [0,0.08,0.12,0.3,0.12,0]
#    qchannel_loss_init = [0,0.01,0.018,0.013,0.013,0.03,0.03,0.012,0.012,0]
#    qchannel_loss_noisy = [0,0.001,0.0018,0.0013,0.003,0.003,0.003,0.0012,0.0012,0]

#### avg 1.47, std 0.46 #####
#    depolar_rates = [0,0.09,0.06,0.31,0.1,0]
#    dephase_rates = [0,0.09,0.06,0.31,0.1,0]
#    qchannel_loss_init = [0,0.01,0.01,0.02,0.006,0.2,0.01,0.012,0.04,0]
#    qchannel_loss_noisy = [0,0.001,0.001,0.002,0.0006,0.02,0.001,0.012,0.004,0]   

#### avg 1.40, std 0.51 #####
#    depolar_rates = [0,0.08,0.01,0.26,0.05,0]
#    dephase_rates = [0,0.08,0.01,0.26,0.05,0]
#    qchannel_loss_init = [0,0.01,0.01,0.001,0.001,0.5,0.03,0.012,0.012,0]
#    qchannel_loss_noisy = [0,0.001,0.001,0.0001,0.001,0.05,0.003,0.0012,0.0012,0]
 
#    path_nodes_number = 7
#
########## avg 1.41, std 0.12 #########
#    depolar_rates = [0,0.1,0.15,0.2,0.18,0.13,0]
#    dephase_rates = [0,0.1,0.15,0.2,0.18,0.13,0]
#    qchannel_loss_init = [0,0.018,0.018,0.015,0.015,0.02,0.02,0.018,0.018,0.001,0.001,0]
#    qchannel_loss_noisy = [0,0.0018,0.0018,0.0015,0.0015,0.002,0.002,0.0018,0.0018,0.0001,0.0001,0]

#    path_nodes_number = 8
#
########## avg 1.41, std 0.12 #########
#    depolar_rates = [0,0.1,0.15,0.2,0.18,0.13,0.14,0]
#    dephase_rates = [0,0.1,0.15,0.2,0.18,0.13,0.14,0]
#    qchannel_loss_init = [0,0.018,0.018,0.015,0.015,0.02,0.02,0.018,0.018,0.001,0.001,0.001,0.1,0]
#    qchannel_loss_noisy = [0,0.0018,0.0018,0.0015,0.0015,0.002,0.002,0.0018,0.0018,0.0001,0.0001,0.0001,0.001,0]

#    path_nodes_number = 9
#
########## avg 1.48, std 0.16 ######### 
#    depolar_rates = [0,0.1,0.15,0.2,0.18,0.25,0.14,0.1,0]
#    dephase_rates = [0,0.1,0.15,0.2,0.18,0.25,0.14,0.1,0]
#    qchannel_loss_init = [0,0.018,0.018,0.015,0.015,0.02,0.02,0.018,0.001,0.03,0.001,0.001,0.1,0.001,0.1,0]
#    qchannel_loss_noisy = [0,0.0018,0.0018,0.0015,0.0015,0.002,0.002,0.0018,0.0001,0.003,0.0001,0.0001,0.001,0.001,0.1,0]

#    path_nodes_number = 10
#
########## avg 1.46, std 0.16 #########
#    depolar_rates = [0,0.1,0.15,0.2,0.18,0.25,0.14,0.1,0.1,0]
#    dephase_rates = [0,0.1,0.15,0.2,0.18,0.25,0.14,0.1,0.1,0]
#    qchannel_loss_init = [0,0.018,0.018,0.015,0.015,0.02,0.02,0.018,0.001,0.03,0.001,0.001,0.1,0.001,0.1,0.1,0.1,0]
#    qchannel_loss_noisy = [0,0.0018,0.0018,0.0015,0.0015,0.002,0.002,0.0018,0.0001,0.003,0.0001,0.0001,0.001,0.001,0.1,0.001,0.01,0]
###########################################################################################################################################################
   
###################################################### initialization ######################################################
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
##############################################################################################################################

########################## pses layer solution test ###########################
    pses_layer_final_solution, pses_layer_final_solution_costs_saving = pses_layer_greedy(path,cost,final_solution=[],final_solution_costs_saving=0)
    entangle_distribution_protocols, entangle_swapping_protocols = define_protocol(pses_layer_final_solution,real_path)
    time_start = time.perf_counter()
    ### call central_controller to exec solution (parallel swapping) ###
    central_controller.parallel_swapping(pses_layer_final_solution, entangle_distribution_protocols, entangle_swapping_protocols, network, False)
    time_stop = time.perf_counter()
    pses_layer_time = time_stop-time_start
    print("cost std is: {}" .format(cost_std))
    print("cost average is: {}" .format(cost_average))
    print("pses layer time is: {}" .format(pses_layer_time))
##############################################################################

########################### imbalanced layer solution test #######################
#    imbalanced_layer_final_solution, imbalanced_layer_final_solution_costs_saving = imbalanced_layer_greedy(path,cost,final_solution=[],final_solution_costs_saving=0)
#    entangle_distribution_protocols, entangle_swapping_protocols = define_protocol(imbalanced_layer_final_solution,real_path)
#    time_start = time.perf_counter()
#    ### call central_controller to exec solution (parallel swapping) ###
#    central_controller.parallel_swapping(imbalanced_layer_final_solution, entangle_distribution_protocols, entangle_swapping_protocols, network, False)
#    time_stop = time.perf_counter()
#    im_layer_time = time_stop-time_start
#    print("cost std is: {}" .format(cost_std))
#    print("cost average is: {}" .format(cost_average))
#    print("im layer time is: {}" .format(im_layer_time))
###########################################################################

########################### pses segment solution test #######################
#    pses_segment_final_solution, pses_segment_final_solution_costs_saving = pses_segment_greedy(path,cost)
#    entangle_distribution_protocols, entangle_swapping_protocols = define_protocol(pses_segment_final_solution,real_path)
#    time_start = time.perf_counter()
#    ### call central_controller to exec solution (parallel swapping) ###
#    central_controller.parallel_swapping(pses_segment_final_solution, entangle_distribution_protocols, entangle_swapping_protocols, network, False)
#    time_stop = time.perf_counter()
#    pses_segment_time = time_stop-time_start
#    print("cost std is: {}" .format(cost_std))
#    print("cost average is: {}" .format(cost_average))
#    print("pses segment time is: {}" .format(pses_segment_time))
###########################################################################

########################### imbalanced segment solution test #######################
#    imbalanced_segment_final_solution, imbalanced_segment_final_solution_costs_saving = imbalanced_segment_greedy(path,cost)
#    entangle_distribution_protocols, entangle_swapping_protocols = define_protocol(imbalanced_segment_final_solution,real_path)
#    time_start = time.perf_counter()
#    ### call central_controller to exec solution (parallel swapping) ###
#    central_controller.parallel_swapping(imbalanced_segment_final_solution, entangle_distribution_protocols, entangle_swapping_protocols, network,False)
#    time_stop = time.perf_counter()
#    im_segment_time = time_stop-time_start
#    print("cost std is: {}" .format(cost_std))
#    print("cost average is: {}" .format(cost_average))
#    print("im segment time is: {}" .format(im_segment_time))
#    print("pses segment time is: {}" .format(pses_segment_time))
###########################################################################

############################ balanced binary tree solution test #######################
#    balanced_final_solution, balanced_final_solution_costs_saving = balanced_binary_tree(path,cost)
#    entangle_distribution_protocols, entangle_swapping_protocols = define_protocol(balanced_final_solution,real_path)
#    time_start = time.perf_counter()
#    ### call central_controller to exec solution (parallel swapping) ###
#    central_controller.parallel_swapping(balanced_final_solution, entangle_distribution_protocols, entangle_swapping_protocols, network, True)
#    time_stop = time.perf_counter()
#    balanced_time = time_stop - time_start
#    print("cost std is: {}" .format(cost_std))
#    print("cost average is: {}" .format(cost_average))
#    print("balanced time is: {}" .format(balanced_time))
############################################################################


