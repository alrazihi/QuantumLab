from qiskit import QuantumCircuit, Aer, execute

# Create a quantum coin flip circuit
qc = QuantumCircuit(1, 1)
qc.h(0)
qc.measure(0, 0)

# Run on simulator
backend = Aer.get_backend('qasm_simulator')
job = execute(qc, backend, shots=10)

# Get counts
print(job.result().get_counts())
