# Kitaev's toric code
A qiskit implementation of Kitaev's toric code



## Motivation 

Kitaev's toric code is a quantum error correction code, modelled on a $$k \times k$$ toric lattice (i.e. with periodic boundary), using $$2 k^{2} $$ physical qubits to encode $$2$$ logical qubits. In other words, the Kitaev toric code is a $$[[2 k^{2} , 2, k]]$$ stabilizer code.

A novel feature of the toric code is that the stabilizer elements are defined with respect the spatial arrangement of qubits situated on a $$ k \times k$$ toric lattice. The arrangement is defined in the following way:


![image](lattice_base.png)

