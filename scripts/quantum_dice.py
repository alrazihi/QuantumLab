from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

# Create a Bell state circuit
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

# Run on simulator
sim = AerSimulator()
result = sim.run(qc, shots=1000).result()

# Get counts - should see {'00': ~500, '11': ~500}
print(result.get_counts())

def roll_die(sim):
    qc = QuantumCircuit(3, 3)
    qc.h([0, 1, 2])        # create uniform superposition over 0-7
    qc.measure([0, 1, 2], [0, 1, 2])
    while True:
        result = sim.run(qc, shots=1).result()
        counts = result.get_counts()
        bitstr = next(iter(counts))  # e.g. '010'
        value = int(bitstr, 2)
        if value < 6:
            return value + 1  # map 0-5 to 1-6

if __name__ == "__main__":
    sim = AerSimulator()
    rolls = [roll_die(sim) for _ in range(10)]
    print("Die rolls:", rolls)