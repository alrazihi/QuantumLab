from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

def quantum_random_bits(n_bits=32):
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.measure(0, 0)
    sim = AerSimulator()
    result = sim.run(qc, shots=n_bits).result()
    counts = result.get_counts()
    # Expand counts into a list of bits (strings '0'/'1')
    bits = []
    for bitstring, cnt in counts.items():
        bits.extend([bitstring] * cnt)
    return bits

if __name__ == "__main__":
    bits = quantum_random_bits(32)
    print("Random bits (len={}):".format(len(bits)))
    print(bits)