from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

# Create a simple circuit
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

# Run on simulator
sim = AerSimulator()
result = sim.run(qc).result()

# Get counts
counts = result.get_counts()
print(counts)
