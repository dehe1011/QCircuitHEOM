<p align="center">
    <img src="docs/figures/logo.png" width="250">
</p>

<p align="center">
    <a href="https://tensorheom.readthedocs.io/en/latest/">
        <img src="https://readthedocs.org/projects/tensorheom/badge/?version=latest"
            alt="Documentation Status" /></a>
    <a href="https://opensource.org/licenses/BSD-3-Clause">
        <img src="https://img.shields.io/badge/license-New%20BSD-blue.svg"
            alt="License"></a>
    <a href='https://github.com/dehe1011/QuantumDNA/actions/workflows/code-quality.yml'>
        <img src='https://img.shields.io/github/actions/workflow/status/dehe1011/QuantumDNA/code-quality.yml?branch=main'
            alt='GitHub Workflow Status' /></a>
    <!-- <a href='https://github.com/psf/black'>
        <img src='https://img.shields.io/badge/code%20style-black-000000.svg'
            alt='Code Style: black' /></a> -->
    <a href="https://pypi.org/project/ttheom/">
        <img src="https://img.shields.io/pypi/v/ttheom.svg"
            alt="PyPI version"></a>
    <a href="https://pypi.org/project/ttheom/">
        <img src="https://img.shields.io/pypi/pyversions/ttheom.svg"
            alt="Python versions"></a>
</p>

---

# TensorHEOM

**Authors: Kiyoto Nakamura, Dennis Herb**

TensorHEOM is a Python package for simulating quantum circuits in non-Markovian environments using free-pole hierarchical equations of motion (FP-HEOM) and tensor-train (TT) compression.

The package is designed for superconducting-qubit simulations and connects circuit-level Qiskit input with microscopic open-system dynamics.

<p align="center">
    <img src="docs/figures/overview.png" width="800">
</p>

## Installation

Install TensorHEOM from PyPI with

```bash
pip install ttheom
```

## Basic usage

A typical workflow is:

1. Define a Qiskit quantum circuit.
2. Specify system, bath, and numerical parameters.
3. Run the TensorHEOM simulation.

```python
from qiskit import QuantumCircuit
from ttheom import calcTimeEvo

qc = QuantumCircuit(1)
qc.h(0)

# expected runtime: 1 min
calcTimeEvo(
   fileName="result",
   qc=qc,
   numQ=1,
   freqQ=[5.0],          # GHz
   rhoIni=[[1,0],[0,0]],
   gateTime=[0.16],      # ns
   idlingTime=0.01,       # ns
   T=30,                 # mK
   T1=32,                # µs
   omegaC=20,
   exp=1/8,
   tol=1e-6,
   dtFB=0.1,             # ps
   depth=[1],
   bondDim=5,
   strideTime=0.01,       # ns
)
```

1. Analyze the pulse sequence, reduced density matrix, and fidelity. For multiple qubits, also analyze concurrence and logarithmic negativity.

```python
import os
from ttheom import *

directory = os.getcwd()
fileName = 'result'

# load kwargs from QPY file 
kwargs = getKwargs(directory, fileName)

# load result from CSV file
t_list, rdo_list = getResult(directory, fileName)

# Post-processing
plotQC(**kwargs)
plotPulseSeq(**kwargs)
plotFidelity(t_list, rdo_list, **kwargs)
plotConcurrence(t_list, rdo_list, **kwargs)
plotLogNeg(t_list, rdo_list, **kwargs)
plotRDO(t_list, rdo_list, **kwargs)
```

## Graphical interface

TensorHEOM also provides a graphical user interface:

```python
from ttheom import TensorHeomApp

TensorHeomApp().mainloop()
```

<p align="center">
    <img src="docs/figures/GUI1.png" width="800">
</p>

## Documentation

[![Documentation Status](https://readthedocs.org/projects/tensorheom/badge/?version=latest)](https://tensorheom.readthedocs.io/en/latest/)

The documentation is available on Read the Docs: https://tensorheom.readthedocs.io/en/latest/

## References

Recent papers from our group:

* K. Nakamura and J. Ankerhold, Entanglement dynamics and performance of two-qubit gates for superconducting qubits under non-Markovian effects. [*Physical Review Research* **8**, 013337 (2026).](https://doi.org/10.1103/b5jp-s6t2)
* K. Nakamura and J. Ankerhold, Impact of time-retarded noise on dynamical decoupling schemes for qubits. [*Physical Review B* **111**, 064503 (2025).](https://doi.org/10.1103/PhysRevB.111.064503)

## License

TensorHEOM is distributed under the BSD 3-Clause License.

## Support

For questions or support, please contact Dennis Herb at dennis.herb@uni-ulm.de.

