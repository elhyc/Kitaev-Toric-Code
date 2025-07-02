# Kitaev's toric code
A qiskit implementation of Kitaev's toric code



## Motivation 

Kitaev's toric code is a quantum error correction code, modelled on a $$k \times k$$ toric lattice (i.e. with periodic boundary), using $$2 k^{2} $$ physical qubits to encode $$2$$ logical qubits. In other words, the Kitaev toric code is a $$[[2 k^{2} , 2, k]]$$ stabilizer code.

A novel feature of the toric code is that the stabilizer elements are defined with respect the spatial arrangement of qubits situated on a $$ k \times k$$ toric lattice. For example, the below image is a $$ 3 \times 3$$ toric lattice: 

<img src="lattice_base.png" alt="lattice" width="100"/>

With respect to this lattice, the physical qubits are placed where the grey dots mark the edges. As the lattice represents a torus and has periodic boundary, the qubits on top and bottom rows are identified, as are the qubits on the left and right outer vertical columns. 
Note that with this arrangement, we have a total of $$2 * 3^{2} = 18$$ qubits.  