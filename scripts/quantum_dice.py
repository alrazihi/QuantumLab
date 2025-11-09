# quantum_dice.py
import random
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from collections import Counter

def roll_die_once():
    sim = AerSimulator()
    qc = QuantumCircuit(3, 3)
    # Put 3 qubits into superposition (0..7)
    for i in range(3):
        qc.h(i)
    qc.measure([0,1,2], [0,1,2])
    # use AerSimulator.run instead of execute/Aer backend
    result = sim.run(qc, shots=1).result()
    counts = result.get_counts()
    measured = list(counts.keys())[0]  # e.g., '010'
    val = int(measured, 2)
    return val

def roll_die():
    # rejection sampling: keep rolling until value in 0..5
    while True:
        v = roll_die_once()
        if v < 6:
            return v + 1  # map 0->1, ..., 5->6

def main():
    n = 20
    rolls = [roll_die() for _ in range(n)]
    print("Dice rolls:", rolls)
    print("Counts:", Counter(rolls))

if __name__ == "__main__":
    main()
