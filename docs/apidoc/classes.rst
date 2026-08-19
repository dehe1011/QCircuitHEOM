Classes & Module Functions
==========================

This section documents internal classes and module-level
functions, grouped by subsystem.

Pulse types and gate specifications
-------------------------------------

.. currentmodule:: qcheom.pulse

.. autofunction:: setGates
.. autofunction:: getGate
.. autoclass:: rxyStep
.. autoclass:: U3Pulse
.. autoclass:: iSwapDPulse
.. autoclass:: directCplStepVarJ

Tensor-train representation
----------------------------

.. currentmodule:: qcheom.tt

.. autoclass:: TTs
.. autoclass:: TTsTwoLevelId
.. autoclass:: TTs1Q
.. autoclass:: TTs2QId
.. autoclass:: TTsMQChainId

Circuit compilation
-------------------

.. currentmodule:: qcheom.circuit

.. autofunction:: setPulseSeq
.. autofunction:: transform
.. autofunction:: scheduling

Time evolution
--------------

.. currentmodule:: qcheom.dynamics

.. autoclass:: timeEvolution
.. autofunction:: zRightOrth
.. autofunction:: calcDynamics
.. autofunction:: outputCurrentStates
.. autofunction:: getRotatingRDO

HPC cluster support
--------------------

.. currentmodule:: qcheom.ssh

.. autofunction:: submitJob
.. autofunction:: downloadResult
.. autofunction:: getClient
.. autofunction:: commandsForSubmission
.. autofunction:: getStatus
.. autofunction:: slurmShell
.. autofunction:: slurmStatus
