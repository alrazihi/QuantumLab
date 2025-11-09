from qiskit.visualization import plot_bloch_multivector
from qiskit.quantum_info import Statevector
from qiskit import QuantumCircuit

# Create a circuit with Hadamard gate
qc = QuantumCircuit(1)
qc.h(0)

# Get statevector and visualize
state = Statevector.from_instruction(qc)
plot_bloch_multivector(state)
