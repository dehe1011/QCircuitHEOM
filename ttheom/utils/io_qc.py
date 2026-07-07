import os
import numpy as np
import qiskit.qpy as qpy

def saveQC(qcFilePath, qc, params):
    """Serialise a quantum circuit and its simulation parameters to a QPY file.

    Parameters
    ----------
    qcFilePath : str
        Destination file path (should end in ``.qpy``).
    qc : qiskit.QuantumCircuit
        Circuit to save.
    params : dict
        Internal parameter dictionary produced by :func:`prepareParams`.

    Returns
    -------
    metadata : dict
        The metadata dict that was stored in ``qc.metadata``.
    """

    metadata = params.copy()
    
    # Prepare rhoIni
    rho = metadata["rho"].copy()
    rhoIni = rho.pop("rhoIni")
    rho["rhoReal"] = rhoIni.real.tolist()
    rho["rhoImag"] = rhoIni.imag.tolist()
    metadata["rho"] = rho

    # Prepare V
    V = metadata.pop("V")
    VTmp = {}
    VTmp["real"] = V.real.tolist()
    VTmp["imag"] = V.imag.tolist()
    metadata["VTmp"] = VTmp
    
    # Save the quantum circuit to a QPY file
    qc.metadata = metadata
    with open(qcFilePath, 'wb') as file:
        qpy.dump(qc, file)
    
    return metadata

def loadQC(qcFilePath):
    """Load a quantum circuit and its simulation parameters from a QPY file.

    Parameters
    ----------
    qcFilePath : str
        Path to the QPY file written by :func:`saveQC`.

    Returns
    -------
    qc : qiskit.QuantumCircuit
        The deserialized quantum circuit.
    params : dict
        Internal parameter dictionary with ``'rhoIni'`` and ``'V'``
        reconstructed as complex NumPy arrays.
    """

    # load the quantum circuit from a QPY file
    with open(qcFilePath, 'rb') as file:
        qc = qpy.load(file)[0]
    metadata = qc.metadata

    # Prepare rhoIni
    rhoTmp = metadata['rho']
    rhoIni = np.array(rhoTmp.pop('rhoReal')) + 1j *np.array(rhoTmp.pop('rhoImag'))
    metadata['rho']['rhoIni'] = rhoIni

    # prepare V
    VTmp = metadata['VTmp']
    V = np.array(VTmp.pop('real')) + 1j * np.array(VTmp.pop('imag'))
    metadata['V'] = V

    params = metadata
    return qc, params