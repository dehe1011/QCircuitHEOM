import os
import getpass

from .bath import getBathParams
from .pulse import setGates
from .tt import TTs1Q, TTs2QId, TTsMQChainId
from .circuit import setPulseSeq
from .dynamics import timeEvolution, outputCurrentStates, calcDynamics
from .ssh import submitJob
from .utils import saveQC, prepareParams

def prepareTTs(**kwargs):
    """Build and initialize the tensor-train data structures for a simulation.

    Parameters
    ----------
    fileName : str
        Base name for the output CSV file.
    directory : str or None, optional
        Output directory. 
    qc : qiskit.QuantumCircuit
        Quantum circuit to be simulated.
    numQ : int
        Number of qubits.
    freqQ : list of float
        Qubit frequencies in GHz.
    rhoIni : numpy.ndarray
        Initial density matrix of shape ``(2**numQ, 2**numQ)``.
    gateTime : list of float
        Gate times in ns.
    idlingTime : float
        Idling time in ns.
    T : float or list of float
        Temperature(s) in mK.
    T1 : float or list of float
        Energy-relaxation time(s) in µs.
    omegaC : float or list of float
        Bath cutoff frequency(ies).
    exp : float or list of float
        Spectral-density exponent(s).
    tol : float or list of float
        AAA tolerance(s) for the bath decomposition.
    dtFB : float
        Integration time step in ps.
    depth : list of int
        FP-HEOM hierarchy depths, one per qubit.
    bondDim : int
        Maximum MPS bond dimension.
    strideTime : float
        Time between successive outputs in ns.
    useRFPlus : bool, optional
        Use the Redfield+ method. Default ``False``.
    isRK13 : bool, optional
        Use the 13-stage Runge-Kutta scheme. Default ``False``.

    Returns
    -------
    TTs : TTs.TTs
        Initialized MPS/MPO object with compiled pulse sequences.
    params : dict
        Simulation parameter dictionary (saved to the ``qpy`` file metadata).
    """

    params = prepareParams(**kwargs)

    # set filepath and save qc data
    fileName, directory = kwargs['fileName'], kwargs.get('directory', None)
    if directory is not None:
        os.makedirs(directory, exist_ok=True)
        qcFilePath = os.path.join(os.getcwd(), directory, 'qcData_' + fileName + '.qpy')
    else:
        qcFilePath = 'qcData_' + fileName + '.qpy'
    qc = kwargs['qc']
    saveQC(qcFilePath, qc, params)
    print(f"Saved quantum circuit data to {qcFilePath}.")

    rho = params["rho"]
    gateList = params["gateList"]
    idlingTime = params["idlingTime"]
    bath = params["bath"]
    dtFB = params["dtFB"]
    depth = params["depth"]
    bondDim = params["bondDim"]
    V = params["V"]

    # Connecting quantum gates and pulse sequence
    pulse, pulseMap = setGates(gateList)

    # Decomposition of bath correlation functions
    nu = []
    coeff = []
    for i in range(rho['numQ']):
        nuTmp, coeffTmp = getBathParams(bath[i])

        nu.append(nuTmp)
        coeff.append(coeffTmp)

    # Initialize Tensor Train structure
    if rho['numQ'] == 1:
        TTs = TTs1Q(rho['rhoIni'], bondDim, V, depth, nu, coeff,
                    pulse, pulseMap)
    elif rho['numQ'] == 2:
        TTs = TTs2QId(rho['rhoIni'], bondDim, V, depth, nu, coeff,
                      pulse, pulseMap)
    elif rho['numQ'] >= 3:
        TTs = TTsMQChainId(rho['numQ'], rho['rhoIni'], bondDim, V, depth,
                           nu, coeff, pulse, pulseMap)
    else:
        raise ValueError(
            f"Invalid number of qubits: expected an integer ≥ 1, got {rho['numQ']}."
        )

    # Compilation qiskit qc into pulse sequence
    _ = setPulseSeq(qc, TTs, rho['omegaQ'], dtFB, idlingTime)

    return TTs, params

def calcTimeEvo(**kwargs):
    """Build the TT structure and run the full time evolution.

    Parameters
    ----------
    fileName : str
        Base name for the output CSV file.
    directory : str or None, optional
        Output directory. 
    qc : qiskit.QuantumCircuit
        Quantum circuit to be simulated.
    numQ : int
        Number of qubits.
    freqQ : list of float
        Qubit frequencies in GHz.
    rhoIni : numpy.ndarray
        Initial density matrix of shape ``(2**numQ, 2**numQ)``.
    gateTime : list of float
        Gate times in ns.
    idlingTime : float
        Idling time in ns.
    T : float or list of float
        Temperature(s) in mK.
    T1 : float or list of float
        Energy-relaxation time(s) in µs.
    omegaC : float or list of float
        Bath cutoff frequency(ies).
    exp : float or list of float
        Spectral-density exponent(s).
    tol : float or list of float
        AAA tolerance(s) for the bath decomposition.
    dtFB : float
        Integration time step in ps.
    depth : list of int
        FP-HEOM hierarchy depths, one per qubit.
    bondDim : int
        Maximum MPS bond dimension.
    strideTime : float
        Time between successive outputs in ns.
    useRFPlus : bool, optional
        Use the Redfield+ method. Default ``False``.
    isRK13 : bool, optional
        Use the 13-stage Runge-Kutta scheme. Default ``False``.
    """

    # Setup tensor trains
    TTs, params = prepareTTs(**kwargs)

    dtFB = params["dtFB"]
    stride = params["stride"]
    isRK13 = params["isRK13"]

    # Set CSV filepath
    fileName, directory = kwargs['fileName'], kwargs.get('directory', None)
    if directory is not None:
        os.makedirs(directory, exist_ok=True)
        csvFilePath = os.path.join(os.getcwd(), directory, fileName + '.csv')
    else:
        csvFilePath = fileName + '.csv'
    print(f"Saved result data to {csvFilePath}.")

    # Time evolution
    timeEvo = timeEvolution(TTs, 0.5*dtFB, isRK13)

    with open(csvFilePath, 'w', encoding='utf-8') as file:
        stepNum = 0
        outputCurrentStates(dtFB, stepNum, TTs, file)
        calcDynamics(dtFB, stride, TTs, timeEvo, file)


def calcTimeEvoHPC(submissionParams, **kwargs):
    """Build the TT structure and submit the full time evolution to HPC.
    
    Parameters
    ----------
    submissionParams : dict
        Submission parameters for the HPC job. User will be prompted to provide OTP.
    fileName : str
        Base name for the output CSV file.
    directory : str or None, optional
        Output directory. 
    qc : qiskit.QuantumCircuit
        Quantum circuit to be simulated.
    numQ : int
        Number of qubits.
    freqQ : list of float
        Qubit frequencies in GHz.
    rhoIni : numpy.ndarray
        Initial density matrix of shape ``(2**numQ, 2**numQ)``.
    gateTime : list of float
        Gate times in ns.
    idlingTime : float
        Idling time in ns.
    T : float or list of float
        Temperature(s) in mK.
    T1 : float or list of float
        Energy-relaxation time(s) in µs.
    omegaC : float or list of float
        Bath cutoff frequency(ies).
    exp : float or list of float
        Spectral-density exponent(s).
    tol : float or list of float
        AAA tolerance(s) for the bath decomposition.
    dtFB : float
        Integration time step in ps.
    depth : list of int
        FP-HEOM hierarchy depths, one per qubit.
    bondDim : int
        Maximum MPS bond dimension.
    strideTime : float
        Time between successive outputs in ns.
    useRFPlus : bool, optional
        Use the Redfield+ method. Default ``False``.
    isRK13 : bool, optional
        Use the 13-stage Runge-Kutta scheme. Default ``False``.

    Returns
    -------
    jobID : str or int
        The job ID returned from the HPC submission.
    """

    params = prepareParams(**kwargs)
    
    # set filepath and save qc data
    fileName, directory = kwargs['fileName'], kwargs.get('directory', None)
    if directory is not None:
        os.makedirs(directory, exist_ok=True)
        qcFilePath = os.path.join(os.getcwd(), directory, 'qcData_' + fileName + '.qpy')
    else:
        qcFilePath = 'qcData_' + fileName + '.qpy'
    qc = kwargs['qc']
    saveQC(qcFilePath, qc, params)
    print(f"Saved quantum circuit data to {qcFilePath}.")

    fileName, directory = kwargs['fileName'], kwargs.get('directory', None)
    qcFilePath = os.path.join(os.getcwd(), directory, 'qcData_' + fileName + '.qpy')
    submissionParams['otp'] = getpass.getpass('Your OTP: ')
    jobID = submitJob(submissionParams, qcFilePath)
    return jobID


def main(fileName, qc, idlingTime, gateList, rho,
         bath, V, dtFB, stride, depth, bondDim, isRK13=False,
         useRFPlus=False):
    """Run the HEOM simulation using pre-assembled internal arguments.

    The reduced density operator time series is written to ``fileName``.

    Parameters
    ----------
    fileName : str
        Path to the output file.
    qc : qiskit.QuantumCircuit
        Quantum circuit to be simulated.
    idlingTime : float
        Idling time in units of ``omegaQ[0]``.
    gateList : list
        List of ``[qubit_indices, gate_type, kwargs]`` entries.
    rho : dict
        System dictionary with keys:

        ``'numQ'`` : int
            Number of qubits.
        ``'rhoIni'`` : numpy.ndarray
            Initial reduced density matrix.
        ``'omegaQ'`` : list of float
            Qubit frequencies normalized by the maximum.

    bath : list of dict
        Bath parameter dictionaries, one per qubit.
    V : numpy.ndarray
        3-D array of system-bath coupling operators;
        ``V[j]`` is the system operator coupled to the ``j``-th bath.
    dtFB : float
        Step width for forward + backward time integration.
    stride : int
        Number of integration steps between successive outputs.
    depth : list of int
        FP-HEOM hierarchy depths.
    bondDim : int
        Maximum MPS bond dimension.
    isRK13 : bool, optional
        Use the 13-stage 5th-order Runge-Kutta scheme (``True``) or the
        5-stage 4th-order scheme (``False``). Default ``False``.
    useRFPlus : bool, optional
        Use the Redfield+ method. Default ``False``.
    """

    if useRFPlus:
        depth  = [1] * len(depth)

    # Decomposition of bath correlation functions
    nu = []
    coeff = []
    for i in range(rho['numQ']):
        nuTmp, coeffTmp = getBathParams(bath[i])

        nu.append(nuTmp)
        coeff.append(coeffTmp)

    # Connecting quantum gates and pulse sequence
    pulse, pulseMap = setGates(gateList)

    # Initialize Tensor Train structure
    if rho['numQ'] == 1:
        TTs = TTs1Q(rho['rhoIni'], bondDim, V, depth, nu, coeff,
                    pulse, pulseMap)
    elif rho['numQ'] == 2:
        TTs = TTs2QId(rho['rhoIni'], bondDim, V, depth, nu, coeff,
                      pulse, pulseMap)
    elif rho['numQ'] >= 3:
        TTs = TTsMQChainId(rho['numQ'], rho['rhoIni'], bondDim, V, depth,
                           nu, coeff, pulse, pulseMap)
    else:
        raise ValueError(
            f"Invalid number of qubits: expected an integer ≥ 1, got {rho['numQ']}."
        )

    # Compilation qiskit qc into pulse sequence
    setPulseSeq(qc, TTs, rho['omegaQ'], dtFB, idlingTime)

    # Time evolution
    timeEvo = timeEvolution(TTs, 0.5*dtFB, isRK13)

    with open(fileName, 'w', encoding='utf-8') as file:
        stepNum = 0
        outputCurrentStates(dtFB, stepNum, TTs, file)
        calcDynamics(dtFB, stride, TTs, timeEvo, file)
