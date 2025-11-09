#!/usr/bin/env python3
"""
grover_vs_classical_demo.py

Educational demo (offline):
- Compare classical brute-force vs Grover's algorithm on small search spaces (1..4 qubits).
- Runs a Grover circuit on a local Qiskit simulator and reports measurement success probability.
- Shows theoretical comparison extrapolated to a 64-bit key (orders of magnitude).

Dependencies:
    pip install qiskit qiskit-aer numpy

Run:
    python grover_vs_classical_demo.py
"""

import math
import random
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

# ---------- Config ----------
SIM = AerSimulator()
MAX_QUBITS = 4   # limit for safety and speed (2^4 = 16 items)
SHOTS = 2000
# ----------------------------

def human_readable_large(n):
    if n == 0:
        return "0"
    for unit in ["", "K", "M", "B", "T", "P", "E"]:
        if abs(n) < 1000:
            return f"{n:.2f}{unit}"
        n /= 1000.0
    return f"{n:.2f}E"

def classical_avg_checks(n_qubits):
    N = 2**n_qubits
    return N / 2.0

def grover_iterations(n_qubits):
    N = 2**n_qubits
    return max(1, int(math.floor((math.pi/4) * math.sqrt(N))))

def build_phase_oracle(n_qubits, target_index, qc, ancillas):
    bits = format(target_index, f'0{n_qubits}b')
    for i, b in enumerate(bits):
        if b == '0':
            qc.x(i)
    if n_qubits == 1:
        qc.z(0)
    elif n_qubits == 2:
        qc.cz(0,1)
    else:
        controls = list(range(0, n_qubits-1))
        target = n_qubits-1
        qc.h(target)
        qc.mcx(controls, target, ancillas, mode='basic')
        qc.h(target)
    for i, b in enumerate(bits):
        if b == '0':
            qc.x(i)

def build_diffusion(n_qubits, qc, ancillas):
    if n_qubits == 0:
        return
    for i in range(n_qubits):
        qc.h(i)
    for i in range(n_qubits):
        qc.x(i)
    if n_qubits == 1:
        qc.z(0)
    elif n_qubits == 2:
        qc.cz(0,1)
    else:
        target = n_qubits - 1
        controls = list(range(0, n_qubits-1))
        qc.h(target)
        qc.mcx(controls, target, ancillas, mode='basic')
        qc.h(target)
    for i in range(n_qubits):
        qc.x(i)
    for i in range(n_qubits):
        qc.h(i)

def run_grover(n_qubits, target_index):
    if n_qubits < 1 or n_qubits > MAX_QUBITS:
        raise ValueError(f"n_qubits must be between 1 and {MAX_QUBITS}")
    N = 2**n_qubits
    ancilla_count = max(0, n_qubits - 2)
    total_qubits = n_qubits + ancilla_count
    qc = QuantumCircuit(total_qubits, n_qubits)
    for i in range(n_qubits):
        qc.h(i)
    r = grover_iterations(n_qubits)
    for _ in range(r):
        build_phase_oracle(n_qubits, target_index, qc, list(range(n_qubits, total_qubits)))
        build_diffusion(n_qubits, qc, list(range(n_qubits, total_qubits)))
    for i in range(n_qubits):
        qc.measure(i, i)
    result = SIM.run(qc, shots=SHOTS).result()
    counts = result.get_counts()
    return counts, r, qc

def demo(n_qubits=2):
    print("=== Grover vs Classical Demo (educational, offline) ===")
    print(f"Using {n_qubits} qubits -> search space size N = 2^{n_qubits} = {2**n_qubits}")
    target = random.randint(0, 2**n_qubits - 1)
    print(f"Random target index chosen (hidden): {target} (binary {format(target, f'0{n_qubits}b')})")
    print()
    classical_checks = classical_avg_checks(n_qubits)
    print("Classical brute-force (average):")
    print(f"  Expected number of checks (avg): {classical_checks:.1f}")
    print()
    counts, r, qc = run_grover(n_qubits, target)
    print("Grover's algorithm (simulated locally):")
    print(f"  Grover iterations r used (oracle calls per run): {r}")
    most_measured, most_count = max(counts.items(), key=lambda kv: kv[1])
    print(f"  Measurement histogram (top outcomes):")
    sorted_counts = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    for s, c in sorted_counts[:min(len(sorted_counts), 8)]:
        print(f"    {s} : {c} counts ({100.0*c/SHOTS:.2f}%)")
    print()
    print(f"  Most-measured bitstring: {most_measured} (decimal {int(most_measured,2)})")
    if int(most_measured,2) == target:
        print("  -> Grover successfully amplified the target to be the most probable outcome.")
    else:
        print("  -> The target is not the most probable result in this run (try increasing shots or rerunning).")
    print()
    print("Circuit (text):")
    print(qc.draw(output='text'))
    print()
    print("----- Theoretical extrapolation (orders of magnitude) -----")
    classical_64_avg = 2**63
    grover_64_oracles = (math.pi/4) * math.sqrt(2**64)
    print(f"Classical average checks for 64-bit key: 2^63 = {classical_64_avg:,} (~{human_readable_large(classical_64_avg)})")
    print(f"Grover oracle calls for 64-bit key (ideal quantum): ~pi/4 * 2^(64/2) = {grover_64_oracles:,.0f} (~{human_readable_large(grover_64_oracles)})")
    print()
    print("Interpretation:")
    print("  - Grover gives a quadratic speedup: it reduces an N search to ~sqrt(N) oracle calls.")
    print("  - Even so, for a 64-bit key the *ideal* Grover oracle calls are ~6.8e9 (billions); building a quantum device to perform")
    print("    that many reliable oracle calls on 64-bit superpositions is far beyond current capability.")
    print("  - Therefore: theoretically weaker, but practically still out of reach today.")
    print("-----------------------------------------------------------")

if __name__ == '__main__':
    try:
        nq = int(input(f"Choose number of qubits for demo (1..{MAX_QUBITS}, default 2): ").strip() or "2")
    except Exception:
        nq = 2
    if nq < 1 or nq > MAX_QUBITS:
        print("Invalid choice, using 2.")
        nq = 2
    demo(nq)
