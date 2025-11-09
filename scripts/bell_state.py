from qiskit import QuantumCircuit, Aer, execute

# Create a Bell state
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)

# Run on simulator
sim = Aer.get_backend('statevector_simulator')
result = execute(qc, sim).result()

# Get statevector
statevector = result.get_statevector()
print(statevector)
