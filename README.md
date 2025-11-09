# Quantum Lab (educational demos)

This repository contains small educational quantum examples and demos (simulated locally). Examples include:
- scripts/quantum_coin_flip.py, bell_state.py, quantum_rng.py, quantum_dice.py, teleportation_demo.py, etc.
- notebooks/ (starter notebooks)
- notes/ (reference PDFs)
- results/ (plots and data)

Important: see DISCLAIMER.txt for legal and safety guidance. This project is for learning only.

## Quick start

1. Install dependencies (recommended in a virtual environment):
```
pip install qiskit qiskit-aer numpy matplotlib
```

2. Run a simple demo (examples use AerSimulator):
```
python d:\QuantumLab\scripts\quantum_coin_flip.py
python d:\QuantumLab\scripts\bell_state.py
python d:\QuantumLab\scripts\quantum_rng.py  # optional args: number_of_bits
python d:\QuantumLab\scripts\teleportation_demo.py
```

3. Grover / password toy demo:
```
python d:\QuantumLab\scripts\quantum_password_demo.py
```

## Notes
- These demos run on a local simulator (qiskit-aer). Ensure qiskit-aer is installed and compatible with your qiskit version.
- Designed for offline educational use; do not use to attack or access systems you do not own.

## License & Responsibility
No license file is included by default. Refer to DISCLAIMER.txt — maintainers accept no liability for misuse.
