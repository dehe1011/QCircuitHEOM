.. _guide:

**********
User Guide
**********

This guide walks through four worked examples that cover the main use-cases of
QCircuitHEOM.  Each page shows how to set up the quantum circuit, run the
simulation locally or on an HPC cluster, reload the results, and compute
physical observables.

.. toctree::
   :maxdepth: 1
   :caption: Examples

   sim_id
   sim_bell
   sim_dd
   sim_ghz

Workflow overview
=================

A typical QCircuitHEOM simulation follows these steps:

.. code-block:: text

   1. Build a Qiskit QuantumCircuit
         ↓
   2. Collect all physical parameters in a kwargs dict
         ↓
   3. Call calcTimeEvo(**kwargs)          ← local run
      or calcTimeEvoHPC(params, **kwargs) ← SLURM submission
         ↓
   4. Load results with getResult()
      Reload circuit + params with getKwargs()
         ↓
   5. Analyse with getFidelity(), getConcurrence(), ...

The function :func:`qcheom.calcTimeEvo` accepts SI-adjacent units (GHz, ns,
mK, µs) and performs all internal unit conversions automatically.
The companion :func:`qcheom.calcTimeEvoHPC` has the same signature but submits
the calculation to a SLURM cluster via SSH and returns the job ID.

HPC workflow
============

For long-running simulations, QCircuitHEOM can submit jobs to a SLURM cluster.

**Step 1: submit**

.. code-block:: python

   import getpass
   from qcheom import calcTimeEvoHPC

   submissionParams = {
       "hostname":      "cluster.example.org",
       "username":      "myuser",
       "password":      "mypassword",
       "schedulerName": "slurm",
       "numNodes":      1,
       "cpusPerTask":   4,
       "maxTime":       "1-00:00:00",
       "venvPath":      "/home/myuser/.venv",
       "emailAddress":  "user@example.org",
       "others":        "",
   }

   job_id = calcTimeEvoHPC(submissionParams, **kwargs)
   print("Submitted job:", job_id)

**Step 2: download**

.. code-block:: python

   import getpass, os
   from qcheom import downloadResult

   directory = ...
   fileName = ...
   csvFilePath = os.path.join(os.getcwd(), directory, fileName + '.csv')

   jobID = "myjobid"

   downloadParams = {
      "hostname":      "cluster.example.org",
      "username":      "myusername",
      "password":      "mypassword",
      "schedulerName": "slurm",
   }
   downloadParams['otp'] = getpass.getpass('Your OTP: ')

   downloadResult(downloadParams, jobID, csvFilePath)

Numerical convergence
=====================

Several parameters dominate simulation accuracy and runtime. Among them are:

``numQ``
    Number of qubits.

``dtFB``
    Time step for the forward-backward propagation.  Smaller values improve
    accuracy but increase runtime.

``depth``
    FP-HEOM hierarchy depth (per qubit).  Depth ``1`` captures leading-order
    system–bath entanglement; depth ``2`` adds second-order corrections.
    Values above ``3`` are rarely needed for weakly coupled baths.

``bondDim``
    Maximum MPS bond dimension.  Larger values capture stronger quantum
    correlations.  For a single qubit and two qubits, ``5``–``20`` is typical.

Redfield+ approximation
=======================

Setting ``useRFPlus=True`` activates the Redfield+ method, a perturbative
approximation that forces ``depth=[1, ...]`` and is much cheaper to run.
It is suitable for large T1 (weak coupling) and serves as a fast sanity check
before launching a full FP-HEOM calculation.
