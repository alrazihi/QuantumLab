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
import hashlib  # Added: map arbitrary password -> index via SHA-256
import base64  # NEW: encode/decode ciphertext
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

# --- New: simple key derivation and XOR-based encrypt/decrypt (educational only) ---
def key_from_bits(bits):
    """Derive 32-byte key from a list of bits using SHA-256 (educational/demo only)."""
    bitstr = ''.join(str(int(b)) for b in bits)
    return hashlib.sha256(bitstr.encode('utf-8')).digest()

def key_from_password_str(pw_str):
    """Derive 32-byte key from an arbitrary password string using SHA-256."""
    return hashlib.sha256(pw_str.encode('utf-8')).digest()

def xor_stream(data_bytes, key_bytes):
    """XOR data_bytes with repeated key_bytes stream."""
    out = bytearray(len(data_bytes))
    klen = len(key_bytes)
    for i, b in enumerate(data_bytes):
        out[i] = b ^ key_bytes[i % klen]
    return bytes(out)

def encrypt_with_bits(bits, plaintext):
    """Encrypt plaintext (str) using bits-derived key; return base64 ciphertext str."""
    key = key_from_bits(bits)
    pt = plaintext.encode('utf-8')
    ct = xor_stream(pt, key)
    return base64.b64encode(ct).decode('ascii')

def decrypt_with_bits(bits, ciphertext_b64):
    """Decrypt base64 ciphertext string using bits-derived key; return plaintext str."""
    try:
        ct = base64.b64decode(ciphertext_b64)
    except Exception:
        raise ValueError("Invalid base64 ciphertext")
    key = key_from_bits(bits)
    pt = xor_stream(ct, key)
    try:
        return pt.decode('utf-8', errors='strict')
    except Exception:
        # return best-effort
        return pt.decode('utf-8', errors='replace')

def encrypt_with_password_str(pw_str, plaintext):
    key = key_from_password_str(pw_str)
    ct = xor_stream(plaintext.encode('utf-8'), key)
    return base64.b64encode(ct).decode('ascii')

def decrypt_with_password_str(pw_str, ciphertext_b64):
    ct = base64.b64decode(ciphertext_b64)
    key = key_from_password_str(pw_str)
    pt = xor_stream(ct, key)
    try:
        return pt.decode('utf-8', errors='strict')
    except Exception:
        return pt.decode('utf-8', errors='replace')
# --- end new helpers ---

# --- New: toy XOR encrypt/decrypt using integer key (small keyspace) ---
def toy_xor_encrypt_int_key(key_int, plaintext):
    """Encrypt plaintext (str) with a single-byte integer key; return base64 ciphertext."""
    key_byte = bytes([key_int & 0xFF])
    ct = xor_stream(plaintext.encode('utf-8'), key_byte)
    return base64.b64encode(ct).decode('ascii')

def toy_xor_decrypt_int_key(key_int, ciphertext_b64):
    """Decrypt base64 ciphertext using single-byte integer key; return plaintext."""
    ct = base64.b64decode(ciphertext_b64)
    key_byte = bytes([key_int & 0xFF])
    pt = xor_stream(ct, key_byte)
    try:
        return pt.decode('utf-8', errors='strict')
    except Exception:
        return pt.decode('utf-8', errors='replace')
# --- end new helpers ---

# ----------------- Main interactive demo -----------------
def main():
    print("=== Quantum Password Demo (educational, offline) ===")
    print("This demo has four independent parts:")
    print("  1) Generate a quantum-random password (bits, hex, ASCII)")
    print("  2) Use Grover's algorithm to amplify the probability of measuring a chosen index in a tiny search space")
    print("  3) Demonstrate Grover's quadratic speedup for key search in a toy XOR cipher (very small keyspace)")
    print("  4) Classical encrypt/decrypt using quantum/random bits or password-derived key")
    print("\nIMPORTANT: Grover's algorithm is probabilistic. For very small search spaces (1–2 qubits),")
    print("the most-measured bitstring should match the target index, but sometimes it may not due to randomness.")
    print("If Grover does not recover the correct key, try increasing the number of shots or rerunning the demo.")
    print("All cryptography here is for educational purposes only and is NOT secure for real use.\n")

    # --- PART 1: Quantum password generation ---
    bit_len = 8
    print("[PART 1] Generating a quantum-random password...")
    pw = generate_quantum_password(bit_len=bit_len)
    print(f"  Bits: {''.join(str(b) for b in pw['bits'])}")
    print(f"  Hex: {pw['hex']}")
    print(f"  ASCII (best-effort): {pw['ascii']}\n")

    # --- PART 2: Grover search for a hidden index ---
    print("[PART 2] Grover search demo (tiny search space)")
    while True:
        try:
            nq = int(input("Choose number of qubits for Grover demo (1 or 2): ").strip() or "2")
        except Exception:
            nq = 2
        if nq in (1,2):
            break
        print("Invalid choice; pick 1 or 2.")
    N = 2**nq

    print("\nHow should Grover's target index be chosen?")
    print("  g - use first {} generated bits (maps bits to integer index)".format(nq))
    print("  c - provide a custom password string (hashed to index mod {})".format(N))
    print("  i - enter target index directly (0..{})".format(N-1))
    choice = input("Select (g/c/i) [g]: ").strip().lower() or "g"

    if choice == 'i':
        while True:
            try:
                target_index = int(input(f"Enter target index (0..{N-1}): ").strip())
                if 0 <= target_index < N:
                    break
            except Exception:
                pass
            print("Invalid index.")
        mapping_info = f"Direct index chosen: {target_index}"
    elif choice == 'c':
        custom = input("Enter custom password string (will be hashed to index): ")
        digest = hashlib.sha256(custom.encode('utf-8')).digest()
        int_val = int.from_bytes(digest, 'big')
        target_index = int_val % N
        mapping_info = f"Custom password hashed to index {target_index} (mod {N}). Grover will search for this index."
    else:
        target_bits = pw['bits'][:nq]
        target_index = int(''.join(str(b) for b in target_bits), 2)
        mapping_info = f"Using first {nq} generated bits {target_bits} -> index {target_index}"

    print("\n[INFO] " + mapping_info)
    print("Grover will amplify the probability of measuring this index in a quantum search.\n")

    counts, iterations, qc = grover_search_demo(n_qubits=nq, target_index=target_index, shots=2048)
    print(f"Grover iterations used: {iterations}")
    print(f"Measurement counts: {counts}")
    best = max(counts.items(), key=lambda kv: kv[1])[0]
    print(f"Most-measured bitstring: {best} (decimal {int(best,2)})")
    if int(best,2) == target_index:
        print("SUCCESS: Grover amplified the target state.")
    else:
        print("NOTE: Grover did not select the target with highest probability in this run.")
        print("      This is expected sometimes due to quantum randomness. Try rerunning or increase shots.")

    # --- PART 3: Toy Grover key-recovery demo ---
    print("\n[PART 3] Toy Grover key-recovery demo (tiny XOR cipher)")
    print("This part demonstrates how Grover's algorithm can be used to recover a secret key in a toy cipher with a very small keyspace.")
    print("You will choose a key size (1 or 2 qubits), encrypt a short message, and Grover will search for the key.")
    if input("Run Grover key-recovery demo on a toy XOR cipher? (y/N): ").strip().lower().startswith('y'):
        while True:
            try:
                kn = int(input("Choose key size for toy Grover (1 or 2 qubits): ").strip() or "2")
            except Exception:
                kn = 2
            if kn in (1,2):
                break
            print("Invalid choice; pick 1 or 2.")
        K = 2**kn
        use_prev = False
        if 0 <= target_index < K:
            use_prev = input(f"Use previously chosen target index {target_index} as key? (y/N): ").strip().lower().startswith('y')
        if use_prev:
            toy_key = target_index
        else:
            toy_key = random.randrange(0, K)
        print(f"Toy secret key (integer in [0..{K-1}]): {toy_key}")

        pt = input("Enter short plaintext to encrypt (default 'HELLO'): ").strip() or "HELLO"
        ct_b64 = toy_xor_encrypt_int_key(toy_key, pt)
        print(f"Toy ciphertext (base64): {ct_b64}")

        print("Running Grover to recover the toy key...")
        counts_k, iters_k, qc_k = grover_search_demo(n_qubits=kn, target_index=toy_key, shots=2048)
        recovered = max(counts_k.items(), key=lambda kv: kv[1])[0]
        rec_int = int(recovered, 2)
        print(f"Grover measurement counts: {counts_k}")
        print(f"Recovered key (most-measured): {recovered} -> int {rec_int}")
        if rec_int == toy_key:
            print("Grover successfully recovered the correct key!")
        else:
            print("Grover did NOT recover the correct key in this run (try increasing shots or rerunning).")

        try:
            dec = toy_xor_decrypt_int_key(rec_int, ct_b64)
            print(f"Decryption with recovered key: {dec}")
        except Exception as e:
            print("Decryption failed:", e)
        print("End of toy Grover key-recovery demo.\n")

    # --- PART 4: Classical encrypt/decrypt demo ---
    print("[PART 4] Classical encrypt/decrypt demo (using quantum/random bits or password-derived key)")
    print("This part lets you encrypt and decrypt messages using either the quantum-generated bits or a password-derived key.")
    use_key_from = "bits"
    if choice == 'c':
        use_key_from = input("Use (b)its-derived key or (p)assword-string key for encrypt/decrypt? [b]: ").strip().lower() or "b"
        key_mode = 'password' if use_key_from.startswith('p') else 'bits'
    else:
        key_mode = 'bits'

    last_cipher = None
    if input("Encrypt a message with the chosen key? (y/N): ").strip().lower().startswith('y'):
        msg = input("Enter plaintext message: ")
        if key_mode == 'password' and choice == 'c':
            ct = encrypt_with_password_str(custom, msg)
        else:
            key_bits = pw['bits'][:max(len(pw['bits']), 8)]
            ct = encrypt_with_bits(key_bits, msg)
        last_cipher = ct
        print(f"Ciphertext (base64): {ct}")

    if input("Decrypt a ciphertext now? (y/N): ").strip().lower().startswith('y'):
        inp = input("Paste ciphertext (base64) [or press Enter to use the last ciphertext]: ").strip()
        if inp == "" and last_cipher is not None:
            inp = last_cipher
        if not inp:
            print("No ciphertext provided.")
        else:
            try:
                if key_mode == 'password' and choice == 'c':
                    pt = decrypt_with_password_str(custom, inp)
                else:
                    key_bits = pw['bits'][:max(len(pw['bits']), 8)]
                    pt = decrypt_with_bits(key_bits, inp)
                print(f"Decrypted plaintext: {pt}")
            except Exception as e:
                print("Decryption failed:", str(e))

    print("\nGrover circuit (text):")
    try:
        print(qc.draw(output='text'))
    except Exception:
        print("(Could not render circuit text)")

    print("\nDemo complete. Reminder: this is a toy demonstration for education. Grover search is probabilistic and works best for larger search spaces and more iterations. All crypto here is for learning only.")

if __name__ == "__main__":
    main()
