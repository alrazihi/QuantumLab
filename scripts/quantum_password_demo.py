#!/usr/bin/env python3
"""
quantum_password_demo.py

Educational demo (offline):
1) Generate quantum-random passwords using a local quantum simulator (Hadamard measurements).
2) Demonstrate Grover's search on a tiny search space (<= 16 items) to find a demo password,
   illustrating how Grover provides a quadratic speedup in the number of oracle queries.

USAGE: python quantum_password_demo.py

DEPENDENCIES (install once, online):
    pip install qiskit qiskit-aer numpy

WARNING: This demo is only for learning on generated/test passwords.
Do NOT use this to attack or access systems you don't own.
"""

import math
import random
import sys
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator  # use AerSimulator for local simulation
from qiskit.quantum_info import Statevector
#from qiskit.visualization import plot_histogram  # optional; not required for headless demo

# -------------- Configuration --------------
SIM = AerSimulator()               # local simulator instance
MAX_GROVER_QUBITS = 4   # maximum qubits for Grover demo => search space size 2^4 = 16
# -------------------------------------------

# Helper: convert bitlist to hex / readable string
def bits_to_hex_str(bits):
    # pack into bytes (MSB first within each byte) and return hex
    n = len(bits)
    # pad to multiple of 8
    pad = (8 - (n % 8)) % 8
    bits = bits + [0] * pad
    b = 0
    out = []
    for i,bit in enumerate(bits):
        b = (b << 1) | int(bit)
        if (i + 1) % 8 == 0:
            out.append(b)
            b = 0
    return ''.join(f"{x:02x}" for x in out)

def bits_to_ascii(bits):
    # try to convert bits to ascii string (8-bit per char)
    pad = (8 - (len(bits) % 8)) % 8
    bits = bits + [0]*pad
    s = ""
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        val = 0
        for bit in byte:
            val = (val << 1) | int(bit)
        if 32 <= val <= 126:
            s += chr(val)
        else:
            s += f"\\x{val:02x}"
    return s

# ----------------- Part 1: Quantum RNG -----------------
def quantum_random_bits(n_bits):
    """
    Generate n_bits using single-qubit Hadamard sampling in batches.
    Uses AerSimulator to get measurement counts and expands them to bits.
    """
    bits = []
    shots = 1024
    runs = math.ceil(n_bits / shots)
    for _ in range(runs):
        # prepare circuit: apply H and measure many times
        qc = QuantumCircuit(1, 1)
        qc.h(0)
        qc.measure(0, 0)
        result = SIM.run(qc, shots=shots).result()
        counts = result.get_counts()
        # counts like {'0': 512, '1': 512}
        for bit_str, cnt in counts.items():
            b = int(bit_str)
            bits.extend([b] * cnt)
            if len(bits) >= n_bits:
                return bits[:n_bits]
    return bits[:n_bits]

def generate_quantum_password(bit_len=32, human_readable=True):
    bits = quantum_random_bits(bit_len)
    hexstr = bits_to_hex_str(bits)
    if human_readable:
        ascii = bits_to_ascii(bits)
        return {
            'bits': bits,
            'hex': hexstr,
            'ascii': ascii
        }
    else:
        return {
            'bits': bits,
            'hex': hexstr
        }

# ------------- Part 2: Toy Grover Demonstration -------------
# We'll implement a simple Grover that searches for a single marked index in a database of size N=2^n.
# Oracle marks one basis state |target>. We'll construct the standard Grover diffusion operator and run
# the algorithm for r ~ floor(pi/4 * sqrt(N)) iterations and show measurement probabilities.

def make_diffusion(n_qubits):
    """Construct standard diffusion (inversion about mean) operator on n_qubits."""
    qc = QuantumCircuit(n_qubits)
    # H on all
    for i in range(n_qubits):
        qc.h(i)
    # X on all
    for i in range(n_qubits):
        qc.x(i)
    # Multi-controlled Z on all-1s
    if n_qubits == 1:
        qc.z(0)
    elif n_qubits == 2:
        qc.cz(0,1)
    else:
        raise NotImplementedError("Diffusion for n_qubits>2 not implemented in this small-demo script.")
    # X on all
    for i in range(n_qubits):
        qc.x(i)
    # H on all
    for i in range(n_qubits):
        qc.h(i)
    return qc

def grover_search_demo(n_qubits=2, target_index=0, shots=1024):
    """
    Run Grover on n_qubits (<= MAX_GROVER_QUBITS) for target_index.
    Returns measurement histogram and number of Grover iterations used.
    """
    if n_qubits > MAX_GROVER_QUBITS:
        raise ValueError(f"n_qubits must be <= {MAX_GROVER_QUBITS} for this demo.")
    if n_qubits not in (1,2):
        raise NotImplementedError("This demo supports only 1 or 2 qubits for Grover to keep it simple and safe.")
    N = 2**n_qubits
    if target_index < 0 or target_index >= N:
        raise ValueError("target_index out of range")

    # Setup: start in uniform superposition
    qc = QuantumCircuit(n_qubits, n_qubits)
    for i in range(n_qubits):
        qc.h(i)

    # Choose iterations r ≈ floor(pi/4 * sqrt(N))
    r = max(1, int(math.floor((math.pi/4) * math.sqrt(N))))
    for _ in range(r):
        # oracle
        if n_qubits == 1:
            # oracle: flip phase of |1> if target==1
            if target_index == 1:
                qc.z(0)
        elif n_qubits == 2:
            bits = format(target_index, '02b')
            # map zeros to X
            for i,b in enumerate(bits):
                if b == '0':
                    qc.x(i)
            # controlled-Z via H+CX+H on last qubit
            qc.h(n_qubits-1)
            qc.cx(0, n_qubits-1)
            qc.h(n_qubits-1)
            # undo X
            for i,b in enumerate(bits):
                if b == '0':
                    qc.x(i)

        # diffusion (inline for small n)
        if n_qubits == 1:
            qc.h(0)
            qc.z(0)
            qc.h(0)
        elif n_qubits == 2:
            for i in range(n_qubits):
                qc.h(i)
                qc.x(i)
            qc.h(n_qubits-1)
            qc.cx(0, n_qubits-1)
            qc.h(n_qubits-1)
            for i in range(n_qubits):
                qc.x(i)
                qc.h(i)

    # Measure
    qc.measure(list(range(n_qubits)), list(range(n_qubits)))
    result = SIM.run(qc, shots=shots).result()
    counts = result.get_counts()
    return counts, r, qc

# ----------------- Main interactive demo -----------------
def main():
    print("=== Quantum Password Demo (educational, offline) ===")
    print("This demo will: (1) generate a quantum-random password, (2) run a tiny Grover search to find it")
    print("Grover demo is limited to n_qubits <= 4 (this script supports 1 or 2 qubits for oracle simplicity).")
    print("Do NOT use this to attack any real systems. Only test on generated demo passwords.")
    print()

    # 1) Generate quantum password
    bit_len = 8  # small bit-length for demo; change upward if you only want rng, but Grover requires small target space
    print(f"Generating a demo password using quantum randomness ({bit_len} bits)...")
    pw = generate_quantum_password(bit_len=bit_len)
    print("Generated (bits):", ''.join(str(b) for b in pw['bits']))
    print("Hex representation:", pw['hex'])
    print("ASCII (best-effort):", pw['ascii'])
    print()

    # 2) Grover demo settings
    while True:
        try:
            nq = int(input("Choose number of qubits for Grover demo (1 or 2; recommended 2): ").strip() or "2")
        except Exception:
            nq = 2
        if nq in (1,2):
            break
        print("Invalid choice; pick 1 or 2.")
    N = 2**nq
    # Map first nq bits to target index
    target_bits = pw['bits'][:nq]
    target_index = int(''.join(str(b) for b in target_bits), 2)
    print(f"Using first {nq} bits of the generated password as the hidden target index: {target_bits} -> {target_index}")
    print("Running Grover (simulated locally) to find the index...")

    counts, iterations, qc = grover_search_demo(n_qubits=nq, target_index=target_index, shots=2048)
    print(f"Grover iterations used (r): {iterations}")
    print("Measurement counts (most-probable state should be the target):", counts)
    try:
        best = max(counts.items(), key=lambda kv: kv[1])[0]
        print(f"Most-measured bitstring: {best} (decimal {int(best,2)})")
        if int(best,2) == target_index:
            print("SUCCESS: Grover amplified the target state.")
        else:
            print("Result did not select target with highest probability (try rerunning or change shots).")
    except Exception:
        pass

    # Optional: show circuit (text)
    print("\nGrover circuit (text):")
    try:
        print(qc.draw(output='text'))
    except Exception:
        print("(Could not render circuit text)")

    print("\nDemo complete. Reminder: this is a toy demonstration for education. Do not misuse.")

if __name__ == "__main__":
    main()
