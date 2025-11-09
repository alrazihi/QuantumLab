# teleportation_demo.py
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, DensityMatrix, partial_trace
import numpy as np

def teleportation(alpha=1.0, beta=0.0):
    # normalize
    norm = np.sqrt(abs(alpha)**2 + abs(beta)**2)
    alpha = alpha / norm
    beta = beta / norm

    # Build circuit that prepares the initial state on q0 and an entangled pair on q1-q2
    c = QuantumCircuit(3)
    c.initialize([alpha, beta], 0)
    c.h(1); c.cx(1, 2)
    # Alice's Bell-basis operations (before measurement)
    c.cx(0, 1); c.h(0)

    # Compute full statevector and density matrix before measurement
    full_sv = Statevector.from_instruction(c)
    # Use DensityMatrix(full_sv) for compatibility across qiskit versions
    dm = DensityMatrix(full_sv).data  # numpy array (8x8)

    results = {}
    for outcome in ['00', '01', '10', '11']:
        # projector on qubits 0 and 1 for the given outcome
        idx = int(outcome, 2)
        e = np.zeros(4, dtype=complex); e[idx] = 1.0
        proj2 = np.outer(e, e.conj())        # 4x4 projector for qubits 0&1
        I = np.eye(2, dtype=complex)         # identity for qubit 2
        proj_full = np.kron(proj2, I)        # 8x8 projector

        # apply projector, renormalize
        dm_proj = proj_full @ dm @ proj_full
        tr = np.trace(dm_proj)
        if abs(tr) < 1e-12:
            results[outcome] = None
            continue
        dm_proj = dm_proj / tr

        # convert to qiskit DensityMatrix and partial-trace out qubits 0 and 1
        dm_q = DensityMatrix(dm_proj)
        reduced = partial_trace(dm_q, [0, 1])  # reduced state of qubit 2
        results[outcome] = reduced

    # Print results
    print("Teleportation results (reduced state of Bob's qubit for each Alice outcome):")
    for k, v in results.items():
        print(k, v)
    print("\nDone. Note: this demo uses statevector/density-matrix math to show teleportation effect.")

if __name__ == "__main__":
    # Example teleport of |+> state
    teleportation(alpha=1.0, beta=1.0)
