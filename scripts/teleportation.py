from qiskit import QuantumCircuit, Aer, execute

# Create a teleportation circuit
qc = QuantumCircuit(3, 1)
qc.h(1)
qc.cx(1, 2)
qc.measure(2, 0)

# Run on simulator
sim = Aer.get_backend('statevector_simulator')
result = execute(qc, sim).result()

# Get statevector
statevector = result.get_statevector()
print(statevector)
