from qiskit.circuit import QuantumCircuit, QuantumRegister, AncillaRegister,ClassicalRegister
from qiskit.quantum_info import Statevector, Operator, partial_trace
from qiskit.circuit import Measure
import itertools
from qiskit_aer import AerSimulator
import matplotlib.pyplot as plt
from qiskit.primitives import SamplerResult
from qiskit.providers.basic_provider import BasicProvider
from qiskit import transpile
import numpy as np
from latticecode import *


def PrepareGroundState(ToricLattice):

    GroundStatePrepQubits = QuantumRegister(ToricLattice.num_of_qubits)
    GroundStatePrep = QuantumCircuit(GroundStatePrepQubits)
    r = ToricLattice.rows
    c = ToricLattice.cols
    
    for i in range(r-1):
        for j in range(c):
            star_list = ToricLattice.get_star_indices(i,j)
            GroundStatePrep.h(star_list[2])
            GroundStatePrep.cx(star_list[2], star_list[0])
            GroundStatePrep.cx(star_list[2], star_list[1])
            GroundStatePrep.cx(star_list[2], star_list[3])
    for k in range(c-1):                
        star_list = ToricLattice.get_star_indices(r-1,k)
        GroundStatePrep.h(star_list[3])
        GroundStatePrep.cx(star_list[3], star_list[0])
        GroundStatePrep.cx(star_list[3], star_list[1])
        GroundStatePrep.cx(star_list[3], star_list[2])
        
    return GroundStatePrep
        
def LogicalX1_circuit(ToricLattice):
    LogicalX1Prep = QuantumCircuit(ToricLattice.num_of_qubits)
    for r in range(ToricLattice.cols):
        LogicalX1Prep.x(r + ToricLattice.cols)
    return LogicalX1Prep


def LogicalX0_circuit(ToricLattice):
    LogicalX0Prep = QuantumCircuit(ToricLattice.num_of_qubits)
    for c in range(ToricLattice.rows):
        LogicalX0Prep.x( 2*c*ToricLattice.rows )
    return LogicalX0Prep




def syndrome_measurement(ToricLattice, LatticeCircuit, shape):
    syndromes = LatticeCircuit.ancillas[:]
    meas = LatticeCircuit.clbits[:]
    DataQubits = LatticeCircuit.qubits[0: 2*ToricLattice.rows * ToricLattice.cols ]
    k=0 
    for i in range(ToricLattice.rows):
        for j in range(ToricLattice.cols):
            
            if shape == 'star':
                S = ToricLattice.get_star_indices(i,j)
            if shape == 'plaquette':
                S = ToricLattice.get_plaquette_indices(i,j)
                
            LatticeCircuit.barrier()
        
            LatticeCircuit.h(syndromes[k])
        
            for idx in S:
                    if shape == 'star':
                        LatticeCircuit.cx( syndromes[k], DataQubits[idx] )
                    if shape == 'plaquette':
                        LatticeCircuit.cz( syndromes[k], DataQubits[idx] )
                        
            LatticeCircuit.h(syndromes[k])
            LatticeCircuit.measure(syndromes[k],meas[k])
            
        ### reset syndromes
            LatticeCircuit.h(syndromes[k])
            
            for idx in S:
                    if shape == 'star':
                        LatticeCircuit.cx( syndromes[k], DataQubits[idx] )
                    if shape == 'plaquette':
                        LatticeCircuit.cz( syndromes[k], DataQubits[idx] )
                        
            LatticeCircuit.h(syndromes[k])    
            k += 1
    
    

def ApplyPauliError(quantum_circuit, qubits, p_error):
    
    
    for qubit in qubits:
        error_choice = np.random.choice([0,1,2,3],p=[1 - p_error, p_error/3, p_error/3, p_error/3])
        if error_choice == 1:
            quantum_circuit.x(qubit)
        if error_choice == 2: 
            quantum_circuit.z(qubit)
        if error_choice == 3:
            quantum_circuit.y(qubit)
    
    
         
def KitaevToricModel( x_0, x_1, k0, k1 , p_error, error=True):

 #### initialize torus data ###
 ##############################
    ToricLattice = Lattice(k0,k1)
    DataQubits= QuantumRegister(ToricLattice.num_of_qubits, name='data')
    LatticeCircuit= QuantumCircuit(DataQubits)
    ToricLattice.populate_plaquettes(LatticeCircuit) 
    ToricLattice.populate_stars(LatticeCircuit)     

##### prepare initial state ####
################################
    LatticeCircuit.compose(PrepareGroundState(ToricLattice),qubits = DataQubits ,inplace = True)
    if x_0 == 1:
        LatticeCircuit.compose( LogicalX0_circuit(ToricLattice),  qubits = DataQubits, inplace = True )
    if x_1 == 1:
        LatticeCircuit.compose( LogicalX1_circuit(ToricLattice),  qubits = DataQubits, inplace = True )
        
    if error == True:
    ###  apply random Pauli channel
        ApplyPauliError(LatticeCircuit, DataQubits, p_error)
        
##### syndrome measurements ##########
####################################
    syndromes = AncillaRegister( ToricLattice.rows * ToricLattice.cols)
    LatticeCircuit.add_register(syndromes)
        
    meas = ClassicalRegister(  ToricLattice.rows * ToricLattice.cols)
    LatticeCircuit.add_register(meas)

    ######### phase flips ###########
    syndrome_measurement(ToricLattice, LatticeCircuit, 'star')


    # simulator = AerSimulator()
    # transpiled_circuit = transpile(LatticeCircuit, simulator)
    # job = simulator.run(transpiled_circuit, shots=1, memory=True)
    # transpiled_circuit = transpile(LatticeCircuit)
    
 
    job = AerSimulator().run(LatticeCircuit, shots=1, memory=True)   
    # job = AerSimulator().run(transpiled_circuit, shots=1, memory=True)
    
    result = job.result()
    # memory = result.get_memory(transpiled_circuit)
    memory = result.get_memory(LatticeCircuit)
    memory_result = memory[0][::-1]
    

    positions = []
    for i in range(len(memory_result)):
        if memory_result[i] == '1':
            positions.append(i)
    

    star_graph = ToricLattice.marked_stars_graph( positions )            

    ## address syndrome 
    star_matchings = nx.min_weight_matching(star_graph,  weight='weight')

    for pair in star_matchings:
        path = ToricLattice.star_path( LatticeCircuit, ToricLattice.stars_lin[pair[0]], ToricLattice.stars_lin[pair[1]] )
        LatticeCircuit.z(path)


    ######### bit flips ###########
    syndrome_measurement(ToricLattice, LatticeCircuit, 'plaquette')
    
    # transpiled_circuit = transpile(LatticeCircuit)
    # job = AerSimulator().run(transpiled_circuit, shots=1, memory=True)
    
    job = AerSimulator().run(LatticeCircuit, shots=1, memory=True)
    result = job.result()
    
    
    # memory = result.get_memory(transpiled_circuit)
    memory = result.get_memory(LatticeCircuit)
    memory_result = memory[0][::-1]


    positions = []
    for i in range(len(memory_result)):
        if memory_result[i] == '1':
            positions.append(i)
            
    # simulator = AerSimulator()
    # job = simulator.run(LatticeCircuit, shots=1)

    plaquette_graph = ToricLattice.marked_plaquettes_graph( positions )
    plaquette_matchings = nx.min_weight_matching(plaquette_graph,  weight='weight')

    for pair in plaquette_matchings:
        path = ToricLattice.plaquette_path( LatticeCircuit, ToricLattice.plaquettes_lin[pair[0]], ToricLattice.plaquettes_lin[pair[1]] )
        LatticeCircuit.x(path)


    ##### final logical Z-parity measurements ####
    ##############################################
    ZReadAncillas = AncillaRegister(2)
    ZReadout = ClassicalRegister(2)

    LatticeCircuit.add_register(ZReadAncillas)
    LatticeCircuit.add_register(ZReadout)

    LatticeCircuit.h(ZReadAncillas[0])
    for i in range(ToricLattice.rows):    
        LatticeCircuit.cz(ZReadAncillas[0], DataQubits[ToricLattice.cols + 2*ToricLattice.cols*i ])
    LatticeCircuit.h(ZReadAncillas[0])  
    LatticeCircuit.measure(ZReadAncillas[0],ZReadout[0])       

    LatticeCircuit.h(ZReadAncillas[1])
    for j in range(ToricLattice.cols):    
        LatticeCircuit.cz(ZReadAncillas[1], DataQubits[ j ] )
    LatticeCircuit.h(ZReadAncillas[1])  
    LatticeCircuit.measure(ZReadAncillas[1],ZReadout[1])      
    ###############
            
            
            
    return LatticeCircuit