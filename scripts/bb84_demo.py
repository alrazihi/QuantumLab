# bb84_demo.py
# Replace deprecated Aer/execute imports with AerSimulator
import random
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from collections import namedtuple

def prepare_qubit(bit, basis):
    # basis: 0 = Z (computational), 1 = X (Hadamard)
    qc = QuantumCircuit(1, 1)
    if bit == 1:
        qc.x(0)
    if basis == 1:
        qc.h(0)
    qc.measure(0, 0)
    return qc

def alice_prepare(bits, bases):
    # returns list of circuits (one-shot each)
    return [prepare_qubit(b, bs) for b, bs in zip(bits, bases)]

def bob_measure(circuits, bob_bases):
    backend = Aer.get_backend('qasm_simulator')
    results = []
    for qc, basis in zip(circuits, bob_bases):
        # to measure in X basis, apply H before measurement
        if basis == 1:
            qc2 = QuantumCircuit(1,1)
            # recreate state: circuits already have the prepare + measure, but prepared with measurement in them.
            # Instead of reusing the prepared circuit (which includes measurement), we will construct a circuit replicating preparation.
            # Simpler approach: build a single circuit for each qubit combining preparation and measurement basis
            # Here we assume `qc` already contains prepare+measure; to simulate measurement in Bob's basis we should have constructed circuits differently.
            pass

    # Simpler (clean) approach: re-implement preparation and measurement per bit:
    alice_bits = [c._data for c in circuits]  # not used - we'll instead rebuild from inputs; so change approach below
    return []

# We'll re-implement cleanly without trying to reuse circuits objects.
def bb84_protocol(n_bits=64):
    sim = AerSimulator()
    # Alice chooses random bits and bases
    alice_bits = [random.randint(0,1) for _ in range(n_bits)]
    alice_bases = [random.randint(0,1) for _ in range(n_bits)]
    # Bob chooses bases
    bob_bases = [random.randint(0,1) for _ in range(n_bits)]
    bob_results = []
    for bit, a_basis, b_basis in zip(alice_bits, alice_bases, bob_bases):
        qc = QuantumCircuit(1,1)
        # Alice prepares
        if bit == 1:
            qc.x(0)
        if a_basis == 1:
            qc.h(0)
        # If Bob measures in X basis, apply H before measurement (to rotate basis)
        if b_basis == 1:
            qc.h(0)
        qc.measure(0,0)
        # use AerSimulator.run instead of execute/Aer backend
        result = sim.run(qc, shots=1).result()
        counts = result.get_counts()
        measured = int(next(iter(counts)))
        bob_results.append(measured)
    # Sifting: keep only positions where bases match
    key_positions = [i for i, (a,b) in enumerate(zip(alice_bases, bob_bases)) if a==b]
    sifted_alice = [alice_bits[i] for i in key_positions]
    sifted_bob   = [bob_results[i] for i in key_positions]
    # Optionally do error-checking: reveal a random subset of bits to estimate error rate
    # For demo, we'll reveal first 10% or at least 1 bit
    reveal_k = max(1, len(sifted_alice)//10)
    reveal_indices = random.sample(range(len(sifted_alice)), reveal_k) if len(sifted_alice)>0 else []
    revealed_alice = [sifted_alice[i] for i in reveal_indices]
    revealed_bob = [sifted_bob[i] for i in reveal_indices]
    # Remove revealed bits from key
    final_alice_key = [b for idx,b in enumerate(sifted_alice) if idx not in reveal_indices]
    final_bob_key   = [b for idx,b in enumerate(sifted_bob) if idx not in reveal_indices]
    return {
        'alice_bits': alice_bits,
        'alice_bases': alice_bases,
        'bob_bases': bob_bases,
        'bob_results': bob_results,
        'sifted_positions': key_positions,
        'sifted_alice': sifted_alice,
        'sifted_bob': sifted_bob,
        'revealed_indices': reveal_indices,
        'revealed_alice': revealed_alice,
        'revealed_bob': revealed_bob,
        'final_alice_key': final_alice_key,
        'final_bob_key': final_bob_key
    }

def bits_to_hex(bits):
    # pack into bytes and return hex
    b = 0
    out = []
    for i,bit in enumerate(bits):
        b = (b << 1) | bit
        if (i+1) % 8 == 0:
            out.append(b)
            b = 0
    # leftover
    rem = (8 - (len(bits)%8)) % 8
    if rem:
        b = b << rem
        out.append(b)
    return ''.join(f"{x:02x}" for x in out)

def main():
    res = bb84_protocol(64)
    print("Alice bases: ", res['alice_bases'])
    print("Bob   bases: ", res['bob_bases'])
    print("Sifted positions (where bases matched):", res['sifted_positions'])
    print("Sifted Alice bits:", res['sifted_alice'])
    print("Sifted Bob bits:  ", res['sifted_bob'])
    print("Revealed indices for error checking:", res['revealed_indices'])
    print("Revealed (Alice,Bob):", list(zip(res['revealed_alice'], res['revealed_bob'])))
    print("Final Alice key (bits):", res['final_alice_key'])
    print("Final Bob   key (bits):", res['final_bob_key'])
    print("Final key (hex):", bits_to_hex(res['final_alice_key']))

if __name__ == "__main__":
    main()
