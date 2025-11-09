from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

# Create a Bell state circuit
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

# Run on simulator
sim = AerSimulator()
result = sim.run(qc, shots=1000).result()

# Get counts - should see {'00': ~500, '11': ~500}
print(result.get_counts())
