import random
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

def bb84_round(sim):
    # Sender
    bit = random.randint(0, 1)
    basis = random.choice(['Z', 'X'])
    qc = QuantumCircuit(1, 1)
    if bit == 1:
        qc.x(0)
    if basis == 'X':
        qc.h(0)
    # Receiver chooses basis
    recv_basis = random.choice(['Z', 'X'])
    if recv_basis == 'X':
        qc.h(0)
    qc.measure(0, 0)
    result = sim.run(qc, shots=1).result().get_counts()
    measured = int(next(iter(result)))
    # Only keep if bases match
    key_bit = bit if basis == recv_basis else None
    return bit, basis, recv_basis, measured, key_bit

if __name__ == "__main__":
    sim = AerSimulator()
    rounds = 20
    kept = []
    for _ in range(rounds):
        bit, b, rb, meas, kb = bb84_round(sim)
        if kb is not None:
            kept.append((kb, meas))
    print("Kept key pairs (sender_bit, receiver_measure):", kept)