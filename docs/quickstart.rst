.. _quickstart:

**********
Quickstart
**********

This page shows the fastest path from installation to a working simulation.

Installation
============

.. code-block:: bash

   pip install qcheom

For detailed installation instructions see :doc:`installation`.

Your first simulation
=====================

The function :func:`qcheom.calcTimeEvo` accepts physical units (GHz, ns, mK, µs)
and writes the time-evolved reduced density matrix to a CSV file.

The example below simulates a single qubit under pi-pulse pairs with broadband Ohmic noise:

.. code-block:: python

   import numpy as np
   from qiskit import QuantumCircuit
   from qcheom import calcTimeEvo

   # Define the quantum circuit
   qc = QuantumCircuit(1)
   qc.rx(np.pi, 0)
   qc.ry(np.pi, 0)

   calcTimeEvo(
       fileName="result_1q",      # output file (result_1q.csv)
       directory="results",       # output directory (optional)
       qc=qc,
       numQ=1,
       freqQ=[5.0],               # qubit frequency in GHz
       rhoIni=[[1, 0], [0, 0]],   # initial state |0⟩⟨0|
       gateTime=[16.0],            # single-qubit gate time in ns
       idlingTime=1.0,             # idling time between gates in ns
       T=30,                       # temperature in mK
       T1=10,                      # energy relaxation time in µs
       omegaC=20,                  # bath cutoff frequency
       exp=1,                      # Ohmic spectral density (s=1)
       tol=1e-6,                   # AAA decomposition tolerance
       dtFB=0.1,                   # time step in ps
       depth=[1],                  # FP-HEOM hierarchy depth
       bondDim=5,                  # maximum MPS bond dimension
       strideTime=0.1,             # output interval in ns
   )

The output CSV contains a time column followed by the real and imaginary parts
of each density-matrix entry.

Reading results
===============

Use :func:`qcheom.getResult` to load the CSV back into Python:

.. code-block:: python

   from qcheom import getResult

   t_list, rdo_list = getResult("results", "result_1q")
   ####### What is "results" and "result_1q"? #######
   # t_list  : 1-D array of time points in units of the largest qubit frequency
   # rdo_list: list of 2×2 density matrices

Analysing results
=================

QCircuitHEOM provides several analysis functions:

.. code-block:: python

    from qcheom import getResult, getKwargs, getFidelity, getConcurrence, getLogarithmicNegativity
    from qiskit.quantum_info import Operator

    # load kwargs from QPY file 
    kwargs = getKwargs("results", "result_bell")

    # load result from CSV file
    t_list, rdo_list = getResult("results", "result_bell")

    # Post-processing
    plotQC(**kwargs)
    plotPulseSeq(**kwargs)
    plotFidelity(t_list, rdo_list, **kwargs)

Submitting to HPC
=================

For long-running calculations, use :func:`qcheom.calcTimeEvoHPC` to submit
the job to a SLURM cluster via SSH:

.. code-block:: python

   from qcheom import calcTimeEvoHPC

   submissionParams = {
       "hostname":      "cluster.example.org",
       "username":      "myuser",
       "password":      "mypassword",
       "schedulerName": "slurm",
       "numNodes":      1,
       "cpusPerTask":   4,
       "maxTime":       "0-04:00:00",
       "venvPath":      "/home/myuser/.venv",
       "emailAddress":  "user@example.org",
       "others":        "",
   }

   job_id = calcTimeEvoHPC(submissionParams, **kwargs)
   print("Job submitted:", job_id)

After the job finishes, download the result with
:func:`qcheom.downloadResult`.

Parameter reference
===================

System
------

``numQ``
    Number of qubits.

``freqQ``
    Qubit transition frequencies in GHz (one per qubit).

``rhoIni``
    Initial density matrix as a 2D list or NumPy array of shape
    ``(2**numQ, 2**numQ)``.

``gateTime``
    Gate durations in ns.  Provide ``numQ`` single-qubit times followed by
    ``numQ-1`` two-qubit times (for a nearest-neighbour chain).

``idlingTime``
    Time inserted between gates in ns (can be ``0`` for no explicit idling).

Bath
----

``T``
    Temperature in mK.  Scalar or list (one per qubit).
    The temperature should be identical with each bath.

``T1``
    Energy-relaxation time in µs.  Scalar or list.

``omegaC``
    Bath cutoff frequency in units of the maximum qubit frequency.

``exp``
    Spectral-density exponent: ``1`` = Ohmic, ``1/2`` = sub-Ohmic, etc.

``tol``
    Tolerance for the AAA bath-decomposition algorithm.
    Typical value: ``1e-6``.

Numerics
--------

``dtFB``
    Forward/backward time step in ps.

``depth``
    FP-HEOM hierarchy depth per qubit (list of int).  ``[1]`` is often
    sufficient for weakly coupled baths.

``bondDim``
    Maximum MPS bond dimension.  Increase for stronger correlations or more
    qubits.

``strideTime``
    Time between output snapshots in ns.

``isRK13``
    Use the 13-stage Runge-Kutta integrator (``True``) or the 5-stage one
    (``False``, default).

``useRFPlus``
    Activate the Redfield+ approximation for a fast, perturbative estimate
    (``False`` by default).

Next steps
==========

- :doc:`guide/guide` — detailed examples for each tutorial scenario
- :ref:`API documentation <apidoc>` — full function and class reference
