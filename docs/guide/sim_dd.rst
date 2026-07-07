.. _sim_dd:

Dynamical Decoupling (single qubit)
=====================================

This example applies XY4 and XY8 dynamical decoupling sequences to a single
qubit and compares how well each sequence preserves coherence against Ohmic
and sub-Ohmic baths.

The full notebook is at ``tutorials/sim_DD.ipynb``.

Background
----------

Dynamical decoupling (DD) refocuses unwanted dephasing by applying a periodic
sequence of π-pulses.  The XY4 sequence (X–Y–X–Y with equal idle intervals)
provides first-order decoupling; XY8 (XY4 repeated twice with reversed order)
gives better performance for certain noise spectra.

Circuit
-------

In Qiskit, idle segments are specified with ``qc.delay(n, 0)`` where ``n``
is an integer number of ``dt`` time units equal to ``dtFB`` ps.

.. code-block:: python

   import numpy as np
   from qiskit import QuantumCircuit

   dtFB = 0.002 / (10 * np.pi * 1e-3)   # ps  (chosen to match internal units)
   idle = int(10 / (1e-3 * dtFB))         # 10 ns expressed in dt units

   # XY4: X – idle – Y – idle, repeated twice
   qc = QuantumCircuit(1)
   for _ in range(2):
       qc.delay(idle, 0)
       qc.rx(np.pi, 0)
       qc.delay(idle, 0)
       qc.ry(np.pi, 0)

Running locally
---------------

.. code-block:: python

   import numpy as np, scipy.constants as c
   from ttheom import calcTimeEvo

   kwargs = {
       "numQ":       1,
       "freqQ":      [5],            # GHz
       "rhoIni":     [[0.5, 0.5],
                      [0.5, 0.5]],  # |+⟩⟨+|
       "gateTime":   [16],           # ns
       "idlingTime": 0,              # ns  (idling built into circuit)
       "T":          c.hbar * 10 * np.pi * 1e9 / (8e-3 * c.k),  # mK
       "T1":         1e-6 / (2 * np.pi) * (2 * np.pi * 1e9) / (10 * np.pi),  # µs
       "omegaC":     50,
       "exp":        1,              # Ohmic
       "tol":        1e-6,
       "dtFB":       dtFB,           # ps
       "depth":      [1],
       "bondDim":    5,
       "strideTime": 0.1,            # ns
   }

   kwargs["directory"] = "results/sim_DD"
   kwargs["fileName"]  = "xy4_s1"
   kwargs["qc"]        = qc

   calcTimeEvo(**kwargs)

For sub-Ohmic noise set ``"exp": 1/8``.  For the XY8 sequence, add a second
block of reversed pulses (Y–X–Y–X) to the circuit before calling
``calcTimeEvo``.

Running on HPC
--------------

.. code-block:: python

   import getpass
   from ttheom import calcTimeEvoHPC

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

Analysis
--------

.. code-block:: python

   import numpy as np, matplotlib.pyplot as plt
   from qiskit.quantum_info import Operator
   from ttheom import getResult, getKwargs, getFidelity

   kwargs   = getKwargs("results/sim_DD", "xy4_s1")
   t_list, rdo_list = getResult("results/sim_DD", "xy4_s1")

   U      = Operator(kwargs["qc"]).data
   target = U @ kwargs["rhoIni"] @ U.conj().T

   fids = [getFidelity(rho, target) for rho in rdo_list]

   plt.plot(t_list, fids)
   plt.xlabel(r"$t$ [ns]")
   plt.ylabel(r"$F$")
   plt.ylim(0, 1.05)
   plt.show()

Off-diagonal coherence (the :math:`\rho_{01}` element) directly reflects
phase memory and is a good indicator of how much DD protects the qubit:

.. code-block:: python

   rho_01_real = [rho[0, 1].real for rho in rdo_list]
   rho_01_imag = [rho[0, 1].imag for rho in rdo_list]
