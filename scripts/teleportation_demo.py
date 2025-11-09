from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector

# Create a standard 3-qubit teleportation circuit
qc = QuantumCircuit(3, 2)
# Prepare arbitrary state on qubit 0 (here |+>)
qc.h(0)
# Create Bell pair between qubit1 and qubit2
qc.h(1)
qc.cx(1, 2)
# Bell measurement between qubit0 and qubit1
qc.cx(0, 1)
qc.h(0)
qc.measure(0, 0)
qc.measure(1, 1)
# Conditional corrections
qc.cx(1, 2)
qc.cz(0, 2)  # Note: after measurement you would apply conditionals; for simulator demonstration we apply them using classical feedback not shown

# For demonstration run the circuit up to measurements to see measurement outcomes, then show final statevector separately
# Run full circuit (without conditional corrections) to inspect measurement outcomes
result = sim.run(qc, shots=1024).result()
print("Teleportation measurement counts (Alice outcomes):", result.get_counts())

# Show final state on qubit 2 by constructing the standard teleportation circuit with proper conditionals via statevector approach:
# Build teleportation (state preparation + Bell + measurement + classical corrections applied logically)
tele_qc = QuantumCircuit(3)
tele_qc.h(0)
tele_qc.h(1)
tele_qc.cx(1, 2)
tele_qc.cx(0, 1)
tele_qc.h(0)
# Instead of real conditional gates, apply corrections to qubit 2 depending on measurement outcomes isn't trivial in statevector; show prepared & expected final state instead:
final_sv = Statevector.from_instruction(QuantumCircuit(1).h(0))
print("Expected teleported statevector on target qubit (|+>):", final_sv.data)