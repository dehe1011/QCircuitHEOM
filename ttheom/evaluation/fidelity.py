import numpy as np
import matplotlib.pyplot as plt
from qiskit.quantum_info import Operator

def getFidelity(rho, sigma):
    """Compute the quantum state fidelity between two density matrices.

    Parameters
    ----------
    rho : numpy.ndarray
        Density matrix; Hermitian, positive semidefinite.
    sigma : numpy.ndarray
        Density matrix; Hermitian, positive semidefinite.

    Returns
    -------
    float
        Fidelity :math:`F(\\rho, \\sigma) = \\left(\\operatorname{tr}\\sqrt{\\sqrt{\\rho}\\,\\sigma\\sqrt{\\rho}}\\right)^2`.
    """
    u, s, v = np.linalg.svd(rho)
    rhoSq = u @ np.diag(np.sqrt(s)) @ v

    u, s, v = np.linalg.svd(sigma)
    sigmaSq = u @ np.diag(np.sqrt(s)) @ v

    norm = np.linalg.norm(rhoSq@sigmaSq, ord='nuc')

    return norm**2

def plotFidelity(t_list, rdo_list, fig=None, ax=None, **kwargs):
    """Plot the quantum state fidelity between a list of density matrices and a target state over time."""

    omegaQ = 2*np.pi*np.array(kwargs['freqQ'])
    omegaQmax = max(omegaQ)
    t = t_list / omegaQmax

    U = Operator(kwargs["qc"]).data
    target = U @ kwargs["rhoIni"] @ U.conj().T

    fids = [getFidelity(rho, target) for rho in rdo_list]

    if fig is None or ax is None:
        fig, ax = plt.subplots()
    ax.plot(t, fids, linewidth=1.5)
    ax.set_xlabel("t [ns]")
    ax.set_ylabel("F")
    ax.set_ylim(-0.02, 1.02)
    ax.grid(True, alpha=0.3)
    return fig, ax

