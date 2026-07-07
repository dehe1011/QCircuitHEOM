import os
import numpy as np
import scipy.constants as c

from .io_qc import loadQC

def prepareSystemParams(numQ, freqQ, rhoIni, gateTime, idlingTime):
    """Build the system dictionary and normalize qubit frequencies.

    Parameters
    ----------
    numQ : int
        Number of qubits.
    freqQ : list of float
        Qubit frequencies in GHz.
    rhoIni : numpy.ndarray, optional
        Initial density matrix of shape ``(2**numQ, 2**numQ)``.
        Defaults to the ground state ``|0><0|``.
    idlingTime : float, optional
        Idling time (unused; reserved for future use).
    gateTime : list of float, optional
        Gate times (unused; reserved for future use).

    Returns
    -------
    omegaQmax : float
        Maximum qubit angular frequency (rad/ns).
    rho : dict
        System dictionary with keys ``'numQ'``, ``'rhoIni'``, ``'omegaQ'``.
    """
    
    # normalize qubit frequencies to the maximum frequency
    omegaQ = 2*np.pi*np.array(freqQ)
    omegaQmax = max(omegaQ)
    omegaQ /= omegaQmax

    # initialize the density matrix
    if rhoIni is None:
        rhoIni = np.zeros((2**numQ, 2**numQ), dtype=np.complex128)
        rhoIni[0, 0] = 1
    else:
        rhoIni = np.array(rhoIni, dtype=np.complex128)
    
    rho = {'numQ': numQ, 'rhoIni': rhoIni, 'omegaQ': omegaQ.tolist()}

    # prepare the gate list for single- and two-qubit gates
    gateList = []
    for i in range(rho['numQ']):
        kwargs1Q = {'omega': float(-rho['omegaQ'][i]), 'gateTime': float(omegaQmax * gateTime[i]) }
        gateList.append([[i], 'rxyStep', kwargs1Q])
    for i in range(rho['numQ']-1):
        kwargs2Q = {'gateTime': float(omegaQmax * gateTime[rho['numQ'] + i]) }
        gateList.append([[i, i+1], 'directCplStepVarJ', kwargs2Q])

    idlingTime *= omegaQmax

    return omegaQmax, rho, gateList, idlingTime

def prepareBathParams(rho, omegaQmax, T, T1, omegaC, exp, tol):
    """Convert physical bath parameters to the internal bath dictionary format.

    Parameters
    ----------
    rho : dict
        System dictionary; ``rho['numQ']`` gives the number of qubits.
    omegaQmax : float
        Maximum qubit angular frequency (GHz), used for unit conversion.
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

    Returns
    -------
    bath : list of dict
        List of bath parameter dictionaries, one per qubit.
    """

    # expand scalars to lists of length numQ
    if not isinstance(T, list) and not isinstance(T, np.ndarray):
        T = [T] * rho['numQ']
    if not isinstance(T1, list) and not isinstance(T1, np.ndarray):
        T1 = [T1] * rho['numQ']
    if not isinstance(omegaC, list) and not isinstance(omegaC, np.ndarray):
        omegaC = [omegaC] * rho['numQ']
    if not isinstance(exp, list) and not isinstance(exp, np.ndarray):
        exp = [exp] * rho['numQ']
    if not isinstance(tol, list) and not isinstance(tol, np.ndarray):
        tol = [tol] * rho['numQ']

    # conversion T -> beta, T1 -> kappa
    beta = c.hbar * omegaQmax * 1e9 / (np.array(T) * 1e-3 * c.k)
    kappa = 1 / (omegaQmax * 1e9 * np.array(T1) * 1e-6 * 2 * np.pi)

    bath = [{'type': 'broadband', 'beta': float(beta[i]), 'kappa': float(kappa[i]),
            'omegaC': omegaC[i], 'exp': exp[i], 'tol': tol[i]} for i in range(rho['numQ'])]
    return bath

def prepareParams(**kwargs):
    """Assemble all internal arguments needed to build the TT structure.

    Parameters
    ----------
    numQ : int
        Number of qubits.
    freqQ : list of float
        Qubit frequencies in GHz.
    gateTime : list of float
        Gate times in ns.
    T : float or list of float
        Temperature(s) in mK.
    T1 : float or list of float
        Energy-relaxation time(s) in µs.
    omegaC : float or list of float
        Bath cutoff frequency(ies).
    exp : float or list of float
        Spectral-density exponent(s).
    tol : float or list of float
        AAA tolerance(s).
    rhoIni : numpy.ndarray
        Initial density matrix.
    idlingTime : float
        Idling time in ns.
    dtFB : float
        Integration time step in fs.
    depth : list of int
        FP-HEOM hierarchy depths.
    bondDim : int
        Maximum MPS bond dimension.

    Returns
    -------
    params : dict
        Internal parameter dictionary with keys ``'omegaQmax'``, ``'rho'``,
        ``'gateList'``, ``'idlingTime'``, ``'bath'``, ``'dtFB'``, ``'depth'``,
        ``'bondDim'``, ``'stride'``, ``'isRK13'``, ``'useRFPlus'``, and ``'V'``.
    """
    
    omegaQmax, rho, gateList, idlingTime = prepareSystemParams(kwargs['numQ'], kwargs['freqQ'], kwargs['rhoIni'], kwargs['gateTime'], kwargs['idlingTime'])
    bath = prepareBathParams(rho, omegaQmax, kwargs['T'], kwargs['T1'], kwargs['omegaC'], kwargs['exp'], kwargs['tol'])

    dtFB = kwargs['dtFB'] * omegaQmax * 1e-3
    stride = int( kwargs['strideTime'] * omegaQmax / dtFB)
    V = np.array([[[0, 1],[1, 0]] for _ in range(rho['numQ'])], dtype=np.complex128)

    # output parameters for simulation
    params = {}
    params['omegaQmax'] = omegaQmax    
    params['rho'] = rho
    params['gateList'] = gateList
    params['idlingTime'] = idlingTime
    params['bath'] = bath
    params['dtFB'] = dtFB
    params['depth'] = kwargs['depth']
    params['bondDim'] = kwargs['bondDim']
    params['stride'] = stride
    params['isRK13'] = kwargs.get('isRK13', False)
    params['useRFPlus'] = kwargs.get('useRFPlus', False)
    params['V'] = V

    return params

def getSystemKwargs(rho, omegaQmax, gateList, idlingTime):
    """Convert internal system parameters back to physical units.

    Parameters
    ----------
    omegaQmax : float
        Maximum qubit angular frequency (rad/ns).
    rho : dict
        Internal system dictionary with keys ``'numQ'``, ``'omegaQ'``,
        ``'rhoReal'``, ``'rhoImag'``.

    Returns
    -------
    numQ : int
        Number of qubits.
    freqQ : list of float
        Qubit frequencies in GHz.
    rhoIni : numpy.ndarray
        Initial density matrix (complex).
    """
    
    numQ = rho['numQ']
    rhoIni = rho['rhoIni']
    freqQ = (np.array(rho['omegaQ']) * omegaQmax / (2*np.pi)).tolist()
    gateTime = [gateList[i][2]['gateTime']/omegaQmax for i in range(2*rho['numQ']-1) ]
    idlingTime /= omegaQmax # ns

    return numQ, freqQ, rhoIni, gateTime, idlingTime

def getBathKwargs(omegaQmax, bath):
    """Convert internal bath parameters back to physical units.

    Parameters
    ----------
    omegaQmax : float
        Maximum qubit angular frequency (rad/ns).
    bath : list of dict
        List of internal bath parameter dictionaries.

    Returns
    -------
    T : numpy.ndarray
        Temperatures in mK.
    T1 : numpy.ndarray
        Energy-relaxation times in µs.
    omegaC : list
        Cutoff frequencies.
    exp : list
        Spectral-density exponents.
    tol : list
        AAA tolerances.
    """
    
    # conversion beta -> T, kappa -> T1
    T = c.hbar * omegaQmax * 1e9 / (np.array([b['beta'] for b in bath]) * 1e-3 * c.k)
    T1 = 1 / (omegaQmax * 1e9 * np.array([b['kappa'] for b in bath]) * 1e-6 * 2 * np.pi)
    
    omegaC = [b['omegaC'] for b in bath]
    exp = [b['exp'] for b in bath]
    tol = [b['tol'] for b in bath]
    return T, T1, omegaC, exp, tol

def getKwargs(directory, fileName):
    """Reconstruct user-facing simulation kwargs from a saved QPY file.

    Parameters
    ----------
    directory : str
        Directory containing the QPY file.
    fileName : str
        Base name of the file (without extension).

    Returns
    -------
    kwargs : dict
        Parameter dictionary in physical units with keys ``'directory'``,
        ``'fileName'``, ``'numQ'``, ``'freqQ'``, ``'rhoIni'``, ``'gateTime'``,
        ``'idlingTime'``, ``'T'``, ``'T1'``, ``'omegaC'``, ``'exp'``, ``'tol'``,
        ``'dtFB'``, ``'depth'``, ``'bondDim'``, ``'strideTime'``, ``'useRFPlus'``,
        ``'isRK13'``, and ``'qc'``.
    """
    
    qcFilePath = os.path.join(os.getcwd(), directory, 'qcData_' + fileName + '.qpy')
    qc, params = loadQC(qcFilePath)
    
    # apply function to prepare system, bath, and gate parameters
    numQ, freqQ, rhoIni, gateTime, idlingTime = getSystemKwargs(params['rho'], params['omegaQmax'], params['gateList'], params['idlingTime'])
    T, T1, omegaC, exp, tol = getBathKwargs(params['omegaQmax'], params['bath'])

    # convert back to physical units
    dtFB =  params['dtFB'] / (1e-3 * params['omegaQmax']) # ps
    strideTime = params['stride'] * params['dtFB'] / params['omegaQmax'] # ns

    kwargs = {
        "directory": directory,
        "fileName": fileName,
        "numQ": numQ,
        "freqQ": freqQ, # GHz
        "rhoIni": rhoIni,
        "gateTime": gateTime, # ns
        "idlingTime": idlingTime, # ns
        "T": T, # mK
        "T1": T1, # us
        "omegaC": omegaC,
        "exp": exp,
        "tol": tol,
        "dtFB": dtFB, # fs
        "depth": params['depth'],
        "bondDim": params['bondDim'],
        "strideTime": strideTime, # ns
        "useRFPlus": params['useRFPlus'],
        "isRK13": params['isRK13'],
    }
    kwargs['qc'] = qc
    return kwargs