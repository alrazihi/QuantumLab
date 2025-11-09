from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

# Create a quantum coin flip circuit
qc = QuantumCircuit(1, 1)
qc.h(0)
qc.measure(0, 0)

# Run on simulator
sim = AerSimulator()
result = sim.run(qc, shots=10).result()  # Added shots=10

# Get counts
print(result.get_counts())
