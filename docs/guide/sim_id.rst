.. _sim_id:

Identity Gate Sequence (single qubit)
======================================

This example simulates a single qubit under a repeated identity-like pulse
sequence (pairs of π-pulses).  It demonstrates that the qubit returns to its
initial state after each pair, and shows how bath non-Markovianity affects the
fidelity decay.

The full notebook is at ``tutorials/sim_Id.ipynb``.

Circuit
-------

Three repetitions of two back-to-back Rx(π) pulses with an idling segment
between each repetition:

.. code-block:: python

   import numpy as np
   from qiskit import QuantumCircuit

   # 10 ns idle expressed in Qiskit delay units (1 dt = dtFB ps)
   dtFB = 0.1             # ps
   idling_manual = int(10 / (1e-3 * dtFB))  # 10 ns

   qc = QuantumCircuit(1)
   for _ in range(3):
       qc.rx(np.pi, 0)
       qc.delay(0, 0)
       qc.rx(np.pi, 0)
       qc.delay(idling_manual, 0)

Running locally
---------------

.. code-block:: python

   from ttheom import calcTimeEvo

   kwargs = {
       "numQ":       1,
       "freqQ":      [5],       # GHz
       "rhoIni":     [[1, 0],
                      [0, 0]],  # |0⟩⟨0|
       "gateTime":   [16],      # ns  (single-qubit gate time)
       "idlingTime": 0,         # ns  (explicit idling handled in circuit)
       "T":          30,        # mK
       "T1":         10,        # µs
       "omegaC":     20,
       "exp":        1,         # Ohmic (s=1)
       "tol":        1e-6,
       "dtFB":       0.1,       # ps
       "depth":      [1],
       "bondDim":    5,
       "strideTime": 0.1,       # ns
   }

   kwargs["directory"] = "results/sim_Id"
   kwargs["fileName"]  = "Id_s1"
   kwargs["qc"]        = qc

   calcTimeEvo(**kwargs)

To explore different bath spectral densities change ``"exp"``
(e.g. ``1/2`` for sub-Ohmic s=1/2, ``1/8`` for s=1/8).

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
   print("Job ID:", job_id)

Download the result after the job finishes:

.. code-block:: python

   import getpass, os
   from ttheom import downloadResult

   directory = "development/results/hpc/sim_Id"
   fileName = "Id_s1"
   csvFilePath = os.path.join(os.getcwd(), directory, fileName + '.csv')

   jobID = "myjobid"

   downloadParams = {
      "hostname":      "cluster.example.org",
      "username":      "myusername",
      "password":      "mypassword",
      "schedulerName": "slurm",
   }
   import getpass
   downloadParams['otp'] = getpass.getpass('Your OTP: ')

   downloadResult(downloadParams, jobID, csvFilePath)

Reloading a saved simulation
-----------------------------

:func:`ttheom.getKwargs` reconstructs the full parameter set from the QPY file
saved alongside the CSV:

.. code-block:: python

   from ttheom import getKwargs

   kwargs = getKwargs("results/sim_Id", "Id_s1")
   # kwargs["qc"]    – the Qiskit circuit
   # kwargs["freqQ"] – qubit frequencies in GHz
   # etc.

Analysis
--------

Compute the gate fidelity with respect to the ideal (noiseless) output state:

.. code-block:: python

   import numpy as np
   from qiskit.quantum_info import Operator
   from ttheom import getResult, getKwargs, getFidelity

   kwargs = getKwargs("results/sim_Id", "Id_s1")
   t_list, rdo_list = getResult("results/sim_Id", "Id_s1")

   # Ideal target: apply the circuit unitarily to the initial state
   U = Operator(kwargs["qc"]).data
   target = U @ kwargs["rhoIni"] @ U.conj().T

   fidelities = [getFidelity(rho, target) for rho in rdo_list]

   import matplotlib.pyplot as plt
   plt.plot(t_list, fidelities)
   plt.xlabel(r"$t$ [ns]")
   plt.ylabel(r"$F$")
   plt.ylim(0, 1.05)
   plt.show()

You can also visualise the full density-matrix evolution:

.. code-block:: python

   from ttheom import plotRDO

   fig, axes = plotRDO(t_list, rdo_list, **kwargs)
   plt.show()
