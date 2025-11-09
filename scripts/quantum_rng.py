# quantum_rng.py
import sys
import math
# Replace deprecated Aer/execute imports with AerSimulator
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import numpy as np

def quantum_bits(n_bits, shots_per_run=1024):
    sim = AerSimulator()
    bits = []
    # We'll generate runs of shots_per_run (speed/memory tradeoff)
    runs = math.ceil(n_bits / shots_per_run)
    for _ in range(runs):
        qc = QuantumCircuit(1, 1)
        qc.h(0)
        qc.measure(0, 0)
        # use AerSimulator.run instead of execute/Aer backend
        result = sim.run(qc, shots=shots_per_run).result()
        counts = result.get_counts()
        # counts returns dict like {'0': 523, '1': 501}
        for bit_str, count in counts.items():
            bits.extend([int(bit_str)] * count)
            if len(bits) >= n_bits:
                return bits[:n_bits]
    return bits[:n_bits]

def bits_to_bytes(bits):
    # pack bits into bytes (MSB first)
    b = bytearray()
    for i in range(0, len(bits), 8):
        byte_bits = bits[i:i+8]
        # pad if necessary
        if len(byte_bits) < 8:
            byte_bits += [0]*(8-len(byte_bits))
        val = 0
        for bit in byte_bits:
            val = (val << 1) | int(bit)
        b.append(val)
    return bytes(b)

def main():
    # Number of random bits to produce:
    n_bits = 256
    if len(sys.argv) > 1:
        n_bits = int(sys.argv[1])
    print(f"Generating {n_bits} random bits (quantum)...")
    bits = quantum_bits(n_bits)
    rnd_bytes = bits_to_bytes(bits)
    print("Random bytes (hex):", rnd_bytes.hex())
    # Example: print first 10 random integers from bytes
    rng = np.frombuffer(rnd_bytes, dtype=np.uint8)
    print("First 10 bytes as integers:", rng[:10].tolist())

if __name__ == "__main__":
    main()
