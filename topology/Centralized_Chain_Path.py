import netsquid as ns
from netsquid.nodes import Node
from netsquid.components import  QuantumMemory, QuantumProcessor
from netsquid.nodes import Network
from netsquid.components.qsource import QSource, SourceStatus
from netsquid.components.qprocessor import QuantumProcessor, PhysicalInstruction
from netsquid.qubits import ketstates as ks
from netsquid.qubits.state_sampler import StateSampler
from netsquid.components.models.delaymodels import FixedDelayModel, FibreDelayModel
from netsquid.components import ClassicalChannel,QuantumChannel
from netsquid.nodes.connections import DirectConnection
from netsquid.components.models.qerrormodels import DepolarNoiseModel, DephaseNoiseModel,FibreLossModel
from netsquid.components import instructions as instr

def Centralized_Cellular_Chain_Path_setup(depolar_rates,dephase_rates,qchannel_loss_init,qchannel_loss_noisy,hops,prep_delay=0,num_mem_positions=3,node_distance=100):
    """
    Create an N-hop path for PSES test.

    Parameters
    ----------
    prep_delay : float, optional
        Delay used in the source in this network. Default is 5 [ns].
    num_mem_positions : int
        Number of memory positions on both nodes in the network. Default is 3.
    depolar_rates : float
        An Array with N items. Depolarization rate of qubits in memory. probability
    dephase_rates : float
        An Array with N items. Dephasing rate of physical measurement instruction. probability
    qchannel_loss_init : float
        An Array with N items. Initial probability of losing a photon once it enters a quantum channel
    qchannel_loss_noisy : float
        An Array with N items. Photon survival probability per channel length [dB/km].
    Returns
    -------
    :class:`~netsquid.components.component.Component`
        A network component with nodes and channels as subcomponents.
    """
    name = globals()
    # Setup Physical Noisy
    ### if time_independent is True then the rate is a probability, if False(default), it is exponential depolarizing rate per unit time [Hz] ###
    for num in range(0,hops):
        measure_noise_model = DephaseNoiseModel(dephase_rate=dephase_rates[num],time_independent=True)
        name['x' + str(num) + '_physical_instructions'] = [
            PhysicalInstruction(instr.INSTR_INIT, duration=3, parallel=True),
            PhysicalInstruction(instr.INSTR_H, duration=1, parallel=True),
            PhysicalInstruction(instr.INSTR_X, duration=1, parallel=True, quantum_noise_model=measure_noise_model),
            PhysicalInstruction(instr.INSTR_Z, duration=1, parallel=True, quantum_noise_model=measure_noise_model),
            PhysicalInstruction(instr.INSTR_S, duration=1, parallel=True),
            PhysicalInstruction(instr.INSTR_SWAP, duration=2),
            PhysicalInstruction(instr.INSTR_MEASURE_BELL, duration=2, paraller=False, quantum_noise_model=measure_noise_model )
        ]
        name['x' + str(num) + '_memory_noise_model'] = DepolarNoiseModel(depolar_rate=depolar_rates[num], time_independent=True)

    measure_noise_model = DephaseNoiseModel(dephase_rate=0,time_independent=True)
    controller_physical_instructions = [
        PhysicalInstruction(instr.INSTR_INIT, duration=3, parallel=True),
        PhysicalInstruction(instr.INSTR_H, duration=1, parallel=True),
        PhysicalInstruction(instr.INSTR_X, duration=1, parallel=True, quantum_noise_model=measure_noise_model),
        PhysicalInstruction(instr.INSTR_Z, duration=1, parallel=True, quantum_noise_model=measure_noise_model),
        PhysicalInstruction(instr.INSTR_S, duration=1, parallel=True),
        PhysicalInstruction(instr.INSTR_SWAP, duration=2),
        PhysicalInstruction(instr.INSTR_MEASURE_BELL, duration=2, paraller=False, quantum_noise_model=measure_noise_model )
    ]
    controller_memory_noise_model = DepolarNoiseModel(depolar_rate=0, time_independent=True)


    # Setup nodes:
    network = Network("Cellura_Network")

    ### Define path nodes ###
    for i in range(0,hops):
        node_name = "x"+str(i)
        qmemory_name = node_name + "_QMemory"
        name[node_name] = network.add_node(node_name)
        name[node_name].add_subcomponent(QuantumProcessor(
                                             qmemory_name, num_mem_positions, memory_noise_models=[name['x' + str(i) + '_memory_noise_model']] * num_mem_positions,
                                             phys_instructions=name['x' + str(i) + '_physical_instructions'],fallback_to_nonphysical=False))

    ### Define Central_Controller ###
    Central_Controller = network.add_node("Central_Controller")

    ### Define Local Domain Controllers ###
    for i in range(0,hops-1):
        controller_name = "c"+str(i)
        node_name_a = "x" + str(i)
        node_name_b = "x" + str(i+1)
        qmemory_name = controller_name + "_QMemory"
        name[controller_name] = network.add_node(controller_name)
        name[controller_name].add_subcomponent(QuantumProcessor(
                                               qmemory_name, num_mem_positions, memory_noise_models=[controller_memory_noise_model] * num_mem_positions,
                                                phys_instructions=controller_physical_instructions, fallback_to_nonphysical=False))
        qsource_name = controller_name + "_" + node_name_a \
                          + "_" + node_name_b + "_" + "QSource"
        name[controller_name].add_subcomponent(QSource(qsource_name, state_sampler=StateSampler([ks.b00]),
                                               num_ports=2, status=SourceStatus.EXTERNAL,
                                               models={"emission_delay_model": FixedDelayModel(delay=prep_delay)}))


    ### Setup classical connections ###
    for i in range(0,hops-1):
        ### define classical channels between local domain controller and central controller ###
        controller_name = "c"+str(i)
        cconnection_name = "CentralController_" + controller_name + "_CConnection"
        cchannel_in_name = "CChannel_" + "CentralController" + "->" + controller_name
        cchannel_out_name = "CChannel" + controller_name + "->" + "CentralController"
        name[cconnection_name] = DirectConnection( cconnection_name,
                                                  ClassicalChannel(cchannel_in_name, length=node_distance,
                                                                  models={"delay_model": FibreDelayModel(c=200e3)}),
                                                  ClassicalChannel(cchannel_out_name, length=node_distance,
                                                                  models={"delay_model": FibreDelayModel(c=200e3)}))
        network.add_connection(Central_Controller, name[controller_name], connection=name[cconnection_name])
        
        ### define classical channels between local domain controller and path nodes ###
        node_name_a = "x" + str(i)
        node_name_b = "x" + str(i+1)
        cconnection_name = controller_name + "_" + node_name_a + "_CConnection"
        cchannel_in_name = "CChannel_" + node_name_a + "->" + controller_name
        cchannel_out_name = "CChannel_" + controller_name + "->" + node_name_a
        name[cconnection_name] = DirectConnection( cconnection_name,
                                              ClassicalChannel(cchannel_in_name, length=node_distance,
                                                              models={"delay_model": FibreDelayModel(c=200e3)}),
                                              ClassicalChannel(cchannel_out_name, length=node_distance,
                                                              models={"delay_model": FibreDelayModel(c=200e3)}))
        network.add_connection(name[node_name_a], name[controller_name], connection=name[cconnection_name])
         
        cconnection_name = controller_name + "_" + node_name_b + "_CConnection"
        cchannel_in_name = "CChannel_" + node_name_b + "->" + controller_name
        cchannel_out_name = "CChannel_" + controller_name + "->" + node_name_b
        name[cconnection_name] = DirectConnection( cconnection_name,
                                              ClassicalChannel(cchannel_in_name, length=node_distance,
                                                              models={"delay_model": FibreDelayModel(c=200e3)}),
                                              ClassicalChannel(cchannel_out_name, length=node_distance,
                                                              models={"delay_model": FibreDelayModel(c=200e3)}))
        network.add_connection(name[node_name_b], name[controller_name], connection=name[cconnection_name])

    ### Create and connect quantum channel, define port name, setup instance quantum port in ###
    ### qin0 in Instance is for receive qubit. And then it will be swap to mem 1 or mem 2 in EntangledDistributionProtocol ###

    for i in range(0,hops-1):
        controller_name = "c"+str(i)
        node_name_a = "x"+str(i)
        node_name_b = "x"+str(i+1)

        qchannel_name = "QChannel_" + controller_name + "_" + node_name_a
        name[qchannel_name] = QuantumChannel(qchannel_name, length=node_distance, models={"delay_model": FibreDelayModel(c=200e3),
                              "quantum_loss_model": FibreLossModel(qchannel_loss_init[2*i], qchannel_loss_noisy[2*i])})
        controller_port_name = "port_name_" + controller_name + "_" + node_name_a
        instance_port_name = "port_name_" + node_name_a + "_" + controller_name
        name[instance_port_name],name[controller_port_name] = network.add_connection(
                                                               name[node_name_a], name[controller_name],
                                                               channel_from=name[qchannel_name], label="quantum")
        name[node_name_a].ports[name[instance_port_name]].forward_input(
                                                               name[node_name_a].qmemory.ports["qin0"])

        qchannel_name = "QChannel_" + controller_name + "_" + node_name_b
        name[qchannel_name] = QuantumChannel(qchannel_name, length=node_distance, models={"delay_model": FibreDelayModel(c=200e3),
                              "quantum_loss_model": FibreLossModel(qchannel_loss_init[(2*i)+1], qchannel_loss_noisy[(2*i)+1])})
        controller_port_name = "port_name_" + controller_name + "_" + node_name_b
        instance_port_name = "port_name_" + node_name_b + "_" + controller_name
        name[instance_port_name],name[controller_port_name] = network.add_connection(
                                                               name[node_name_b], name[controller_name],
                                                               channel_from=name[qchannel_name], label="quantum")
        name[node_name_b].ports[name[instance_port_name]].forward_input(
                                                               name[node_name_b].qmemory.ports["qin0"])
        

    ### Setup Controller quantum port out ###
    for i in range(0,hops-1):
        controller_name = "c"+str(i)
        node_name_a = "x"+str(i)
        node_name_b = "x"+str(i+1)

        qsource_name = controller_name + "_" + node_name_a \
                        + "_" + node_name_b + "_" + "QSource"
        controller_port_name_1 = "port_name_" + controller_name + "_" + node_name_a
        controller_port_name_2 = "port_name_" + controller_name + "_" + node_name_b
        name[controller_name].subcomponents[qsource_name].ports["qout0"].forward_output(
                 name[controller_name].ports[name[controller_port_name_1]])
        name[controller_name].subcomponents[qsource_name].ports["qout1"].forward_output(
                 name[controller_name].ports[name[controller_port_name_2]])

    ### return network ###
    return network

#depolar_rates = [0,0.2,0.1,0.2,0.04,0]
#dephase_rates = [0,0.3,0.1,0.1,0.4,0]
#qchannel_loss_init = [0,0,0,0,0,0,0,0,0,0]
#qchannel_loss_noisy = [0,0,0,0,0,0,0,0,0,0]
#network = Centralized_Cellular_Chain_Path_setup(depolar_rates=depolar_rates,dephase_rates=dephase_rates,qchannel_loss_init=qchannel_loss_init,qchannel_loss_noisy=qchannel_loss_noisy, hops=6)
#for conn in network.connections.values():
#    print(conn)
#for node in network.nodes.values():
#    print(node.name, node.qmemory)


