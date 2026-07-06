.. _sim_ghz:

GHZ State (three qubits)
=========================

This example prepares the three-qubit GHZ state
:math:`|\text{GHZ}\rangle = (|000\rangle + |111\rangle)/\sqrt{2}` using a
Hadamard gate and two CNOTs, then studies how multipartite entanglement
decays under non-Markovian noise.

The full notebook is at ``tutorials/sim_GHZ.ipynb``.

Circuit
-------

.. code-block:: python

   from qiskit import QuantumCircuit

   qc = QuantumCircuit(3)
   qc.h(0)
   qc.cx(0, 1)
   qc.cx(1, 2)

Running locally
---------------

.. code-block:: python

   from ttheom import calcTimeEvo

   kwargs = {
       "numQ":       3,
       "freqQ":      [5, 5, 5],          # GHz
       "rhoIni":     [[1, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0]],   # |000⟩⟨000|
       "gateTime":   [16, 16, 16, 50, 50],  # ns  (3 × 1Q + 2 × 2Q)
       "idlingTime": 0,                     # ns
       "T":          30,                    # mK
       "T1":         32,                    # µs
       "omegaC":     20,
       "exp":        1 / 2,                 # sub-Ohmic (s=1/2)
       "tol":        1e-6,
       "dtFB":       0.1,                   # ps
       "depth":      [1, 1, 1],
       "bondDim":    5,
       "strideTime": 0.1,                   # ns
   }

   kwargs["directory"] = "results/sim_GHZ"
   kwargs["fileName"]  = "GHZ_s2"
   kwargs["qc"]        = qc

   calcTimeEvo(**kwargs)

For a three-qubit chain ``gateTime`` has three single-qubit entries (one per
qubit) followed by two two-qubit entries (Q0–Q1 and Q1–Q2).

Running on HPC
--------------

.. code-block:: python

   import getpass
   from ttheom import calcTimeEvoHPC

   submissionParams = {
       "hostname":      "cluster.example.org",
       "username":      "myuser",
       "password":      getpass.getpass("Password: "),
       "schedulerName": "slurm",
       "numNodes":      1,
       "cpusPerTask":   1,
       "maxTime":       "336:00:00",
       "venvPath":      "/home/myuser/.venv",
       "emailAddress":  "user@example.org",
       "others":        "",
   }

   job_id = calcTimeEvoHPC(submissionParams, **kwargs)

Analysis
--------

The logarithmic negativity with respect to different bipartitions quantifies
which pairs of qubits remain entangled over time:

.. code-block:: python

   import matplotlib.pyplot as plt
   from qiskit.quantum_info import Operator
   from ttheom import (getResult, getKwargs, getFidelity,
                       getLogarithmicNegativity)

   kwargs   = getKwargs("results/sim_GHZ", "GHZ_s2")
   t_list, rdo_list = getResult("results/sim_GHZ", "GHZ_s2")

   U      = Operator(kwargs["qc"]).data
   target = U @ kwargs["rhoIni"] @ U.conj().T

   fid_list = [getFidelity(rho, target) for rho in rdo_list]

   # Logarithmic negativity for the 1|23, 2|13, and 3|12 bipartitions
   en_1 = [getLogarithmicNegativity(rho, transposeQIdx=[0]) for rho in rdo_list]
   en_2 = [getLogarithmicNegativity(rho, transposeQIdx=[1]) for rho in rdo_list]
   en_3 = [getLogarithmicNegativity(rho, transposeQIdx=[2]) for rho in rdo_list]

   fig, axes = plt.subplots(4, 1, sharex=True, figsize=(5, 7))
   axes[0].plot(t_list, fid_list);  axes[0].set_ylabel("Fidelity")
   axes[1].plot(t_list, en_1);      axes[1].set_ylabel(r"$E_N^{1|23}$")
   axes[2].plot(t_list, en_2);      axes[2].set_ylabel(r"$E_N^{2|13}$")
   axes[3].plot(t_list, en_3);      axes[3].set_ylabel(r"$E_N^{3|12}$")
   axes[-1].set_xlabel("t [ns]")
   plt.tight_layout()
   plt.show()
