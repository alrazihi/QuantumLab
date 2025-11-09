# entanglement_visualizer.py
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector, partial_trace
from qiskit.visualization import plot_bloch_multivector
import matplotlib.pyplot as plt
import numpy as np

def create_bell_state():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    return qc

def measure_bell_counts(shots=1024):
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0,1)
    qc.measure([0,1],[0,1])
    sim = AerSimulator()
    result = sim.run(qc, shots=shots).result()
    return result.get_counts()

def save_bloch_states(qc, filename_prefix="bell"):
    # get full statevector after building bell (no measurement)
    state = Statevector.from_instruction(qc)
    # partial traces
    rho0 = partial_trace(state, [1])  # qubit 0
    rho1 = partial_trace(state, [0])  # qubit 1
    # convert to statevector for Bloch plotting
    sv0 = state.data.reshape(-1)[:2]  # not exact - better to derive reduced state vector using eigen
    # We'll use plot_bloch_multivector on the full state but for each qubit use reduced statevector via Statevector?
    # Qiskit's plot_bloch_multivector accepts Statevector of full system and will show multi qubit bloch if given
    # Use single-qubit statevectors from density matrices (extract eigenvector of rho)
    def density_to_statevec(rho):
        # take eigenvector with largest eigenvalue (pure-ish approximation)
        vals, vecs = np.linalg.eigh(rho.data)
        idx = np.argmax(vals)
        vec = vecs[:, idx]
        return vec
    v0 = density_to_statevec(rho0)
    v1 = density_to_statevec(rho1)
    # plot and save
    fig0 = plot_bloch_multivector(v0)
    fig0.savefig(f"{filename_prefix}_qubit0_bloch.png")
    plt.close(fig0)
    fig1 = plot_bloch_multivector(v1)
    fig1.savefig(f"{filename_prefix}_qubit1_bloch.png")
    plt.close(fig1)
    print(f"Saved {filename_prefix}_qubit0_bloch.png and {filename_prefix}_qubit1_bloch.png")

def main():
    qc = create_bell_state()
    print("Bell state circuit:")
    print(qc.draw())
    counts = measure_bell_counts(shots=1024)
    print("Measurement counts (should be mostly '00' and '11'):", counts)
    # Save Bloch sphere images
    save_bloch_states(qc, "bell")
    print("Done.")

if __name__ == "__main__":
    main()
