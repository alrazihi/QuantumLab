from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector

# Create a Bell state circuit
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

# Run on simulator
sim = AerSimulator()
result = sim.run(qc, shots=1024).result()
print("Measurement counts (Bell state):", result.get_counts())

# Also show the statevector amplitudes
sv = Statevector.from_instruction(QuantumCircuit(2).h(0).cx(0, 1))
print("Statevector amplitudes:", sv.data)