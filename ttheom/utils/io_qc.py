import os
import numpy as np
import qiskit.qpy as qpy

def saveQC(qcFilePath, qc, params):

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