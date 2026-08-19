import numpy as np
import matplotlib.pyplot as plt

def getLogarithmicNegativity(rho, transposeQIdx):
    """Compute the logarithmic negativity of a multi-qubit density matrix.

    Parameters
    ----------
    rho : numpy.ndarray
        Density matrix of shape ``(2**N, 2**N)``.
        Row/column ordering: qubit ``N-1`` is the most significant index,
        qubit ``0`` is the least significant.
    transposeQIdx : list of int
        Indices of qubits on which the partial transpose is performed.

    Returns
    -------
    float
        Logarithmic negativity :math:`E_N(\\rho) = \\log_2 \\|\\rho^{T_A}\\|_1`.
    """

    numQ = int(np.log2(rho.shape[0]))

    tensorDims = [2] * 2 * numQ

    rhoTensor = rho.reshape(tensorDims)

    perm = np.arange(2*numQ)

    for q in transposeQIdx:
        rowAxis = numQ - 1 - q
        colAxis = rowAxis + numQ

        perm[rowAxis], perm[colAxis] = (perm[colAxis], perm[rowAxis])

    rhoTensorPartTrans = np.transpose(rhoTensor, perm)

    rhoPartTrans = rhoTensorPartTrans.reshape((2**numQ, 2**numQ))

    vals = np.linalg.svd(rhoPartTrans, compute_uv=False)

    traceNorm = np.sum(vals).real
    traceNorm = max(traceNorm, 1.0)

    return np.log2(traceNorm)

def plotLogNeg(t_list, rdo_list, transposeQIdx=[0], fig=None, ax=None, **kwargs):
    """Plot the logarithmic negativity of a list of multi-qubit density matrices over time."""

    if kwargs['numQ'] < 2:
        print("Logarithmic negativity is only defined for multi-qubit density matrices.")
        return

    omegaQ = 2*np.pi*np.array(kwargs['freqQ'])
    omegaQmax = max(omegaQ)
    t = t_list / omegaQmax

    log_neg = [getLogarithmicNegativity(rho, transposeQIdx=transposeQIdx) for rho in rdo_list]

    if fig is None or ax is None:
        fig, ax = plt.subplots()
    ax.plot(t, log_neg, linewidth=1.5)
    ax.set_xlabel("t [ns]")
    ax.set_ylabel("E_N")
    ax.set_ylim(-0.02, max(log_neg) + 0.1)
    ax.grid(True, alpha=0.3) 
    return fig, ax