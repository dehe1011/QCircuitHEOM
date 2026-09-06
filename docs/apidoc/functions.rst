Top-level Functions
===================

This section documents the public functions available at the top level (i.e., importable directly via ``from qcheom import ...``).

High-level simulation interface
--------------------------------

.. currentmodule:: qcheom.main

.. autofunction:: prepareTTs
.. autofunction:: calcTimeEvo
.. autofunction:: calcTimeEvoHPC

Physical-unit helpers
----------------------

.. currentmodule:: qcheom.utils.prepare

.. autofunction:: prepareParams
.. autofunction:: prepareSystemParams
.. autofunction:: prepareBathParams
.. autofunction:: getKwargs
.. autofunction:: getSystemKwargs
.. autofunction:: getBathKwargs

I/O utilities
-------------

.. currentmodule:: qcheom.utils.io_qc

.. autofunction:: saveQC
.. autofunction:: loadQC

.. currentmodule:: qcheom.utils.io_csv

.. autofunction:: getResult
.. autofunction:: loadCSV

Bath decomposition
------------------

.. currentmodule:: qcheom.bath

.. autofunction:: getBathParams
.. autofunction:: broadbandNoise

Evaluation and analysis
-----------------------

.. currentmodule:: qcheom.evaluation

.. autofunction:: getFidelity
.. autofunction:: getConcurrence
.. autofunction:: getLogarithmicNegativity
.. autofunction:: plotPulseSeq
.. autofunction:: plotRDO
.. autofunction:: plotQC
