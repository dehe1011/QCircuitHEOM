.. _sim_bell:

Bell State (two qubits)
========================

This example prepares the Bell state
:math:`|\Phi^+\rangle = (|00\rangle + |11\rangle)/\sqrt{2}` using a Hadamard
gate followed by a CNOT, and tracks fidelity, concurrence, and logarithmic
negativity as entanglement decays under non-Markovian noise.

The full notebook is at ``tutorials/sim_Bell.ipynb``.

Circuit
-------

.. code-block:: python

   from qiskit import QuantumCircuit

   qc = QuantumCircuit(2)
   qc.h(0)
   qc.cx(0, 1)

Running locally
---------------

.. code-block:: python

   from qcheom import calcTimeEvo

   kwargs = {
       "numQ":       2,
       "freqQ":      [5, 5],        # GHz
       "rhoIni":     [[1, 0, 0, 0],
                      [0, 0, 0, 0],
                      [0, 0, 0, 0],
                      [0, 0, 0, 0]],  # |00⟩⟨00|
       "gateTime":   [16, 16, 50],  # ns  (2 × 1Q + 1 × 2Q)
       "idlingTime": 1,             # ns
       "T":          30,            # mK
       "T1":         1,             # µs
       "omegaC":     20,
       "exp":        1,             # Ohmic (s=1)
       "tol":        1e-6,
       "dtFB":       0.1,           # ps
       "depth":      [1, 1],
       "bondDim":    5,
       "strideTime": 0.1,           # ns
   }

   kwargs["directory"] = "results/sim_Bell"
   kwargs["fileName"]  = "Bell_s1"
   kwargs["qc"]        = qc

   calcTimeEvo(**kwargs)

``gateTime`` contains ``numQ`` single-qubit gate times followed by
``numQ-1`` two-qubit gate times.  Here that is two 1Q gates (16 ns each) and
one 2Q coupling gate (50 ns).

Running on HPC
--------------

.. code-block:: python

   import getpass
   from qcheom import calcTimeEvoHPC

   submissionParams = {
       "hostname":      "cluster.example.org",
       "username":      "myuser",
       "password":      "mypassword",
       "schedulerName": "slurm",
       "numNodes":      1,
       "cpusPerTask":   1,
       "maxTime":       "336:00:00",
       "venvPath":      "/home/myuser/.venv",
       "emailAddress":  "user@example.org",
       "others":        "",
   }

   job_id = calcTimeEvoHPC(submissionParams, **kwargs)
   print("Job ID:", job_id)

Analysis
--------

.. code-block:: python

   import numpy as np
   from qiskit.quantum_info import Operator
   from qcheom import (getResult, getKwargs, getFidelity,
                       getConcurrence, getLogarithmicNegativity)

   kwargs    = getKwargs("results/sim_Bell", "Bell_s1")
   t_list, rdo_list = getResult("results/sim_Bell", "Bell_s1")

   # Ideal Bell state (noiseless unitary output)
   U      = Operator(kwargs["qc"]).data
   target = U @ kwargs["rhoIni"] @ U.conj().T

   fid_list     = [getFidelity(rho, target) for rho in rdo_list]
   conc_list    = [getConcurrence(rho) for rho in rdo_list]
   log_neg_list = [getLogarithmicNegativity(rho, transposeQIdx=[0])
                   for rho in rdo_list]

   import matplotlib.pyplot as plt
   fig, axes = plt.subplots(3, 1, sharex=True)
   axes[0].plot(t_list, fid_list);  axes[0].set_ylabel(r"$F$")
   axes[1].plot(t_list, conc_list); axes[1].set_ylabel(r"$C$")
   axes[2].plot(t_list, log_neg_list); axes[2].set_ylabel(r"$E_N$")
   axes[-1].set_xlabel(r"$t$ [ns]")
   plt.tight_layout()
   plt.show()
