Top-level Functions
===================

This section documents the public functions available at the top level (i.e., importable directly via ``from ttheom import ...``).

High-level simulation interface
--------------------------------

.. currentmodule:: ttheom.main

.. autofunction:: prepareTTs
.. autofunction:: calcTimeEvo
.. autofunction:: calcTimeEvoHPC

Physical-unit helpers
----------------------

.. currentmodule:: ttheom.utils.prepare

.. autofunction:: prepareParams
.. autofunction:: prepareSystemParams
.. autofunction:: prepareBathParams
.. autofunction:: getKwargs
.. autofunction:: getSystemKwargs
.. autofunction:: getBathKwargs

I/O utilities
-------------

.. currentmodule:: ttheom.utils.io_qc

.. autofunction:: saveQC
.. autofunction:: loadQC

.. currentmodule:: ttheom.utils.io_csv

.. autofunction:: getResult
.. autofunction:: loadCSV

Bath decomposition
------------------

.. currentmodule:: ttheom.bath

.. autofunction:: getBathParams
.. autofunction:: broadbandNoise

Evaluation and analysis
-----------------------

.. currentmodule:: ttheom.evaluation

.. autofunction:: getFidelity
.. autofunction:: getConcurrence
.. autofunction:: getLogarithmicNegativity
.. autofunction:: plotPulseSeq
.. autofunction:: plotRDO
.. autofunction:: plotQC
