import qutip as q
import numpy as np
import scipy.linalg as la

from .oqs import (
    Kraus_to_STM,
    STM_to_Choi,
    is_trace_preserving,
)

offset = 1e-15
verbose = False

# ----------------------------------------------------------------------
# [1] Hashim 2024, arXiv:2408.12064v1
# [2] Rossini et al. 2023, DOI: 10.1103/PhysRevLett.131.110603
# [3] Ruskai et al. 2002, DOI: 10.1016/S0024-3795(01)00547-X
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# 1. Construct the PTM for the forward map by process tomography
# ----------------------------------------------------------------------


def construct_PTM(input_array):
    """Construct the PTM from the results of the process tomography as described in section VII.B in Hashim2024.
    input_array
        1st dimension: pauli eigenstates as initial states in order zp, zm, xp, yp (see Eq. (308) in Hashim2024).
        2nd dimension: pauli observables in order X, Y, Z (see Eq. (309) in Hashim2024).
        3rd dimension: timesteps.
    """

    # remove the first column of the input array
    input_array = input_array[:, :, 1:]

    n_timesteps = input_array.shape[-1]
    PTM_list = np.zeros((4, 4, n_timesteps))

    PTM_list[0, 0, :] = 1  # first column is (1,0,0,0) because the map is TP
    for i in range(3):
        zp, zm, xp, yp = (
            input_array[0, i, :],
            input_array[1, i, :],
            input_array[2, i, :],
            input_array[3, i, :],
        )
        PTM_list[i + 1, 0, :] = 0.5 * (zp + zm)  # identity
        PTM_list[i + 1, 1, :] = 0.5 * (2 * xp - zp - zm)  # sigma_x
        PTM_list[i + 1, 2, :] = 0.5 * (2 * yp - zp - zm)  # sigma_y
        PTM_list[i + 1, 3, :] = 0.5 * (zp - zm)  # sigma_z
    return PTM_list

# ----------------------------------------------------------------------
# 2. Construct the PTM for the backward map
# ----------------------------------------------------------------------


def invert_PTM(PTM):
    """Construct the inverse PTM to invert the map."""

    PTM_inv = np.zeros((4, 4))
    PTM_inv[0, 0] = 1  # top-left stays 1

    t = PTM[1:, 0]
    R = PTM[1:, 1:]
    R_inv = np.linalg.inv(R)
    t_inv = -np.dot(R_inv, t)

    PTM_inv[1:, 0] = t_inv
    PTM_inv[1:, 1:] = R_inv

    return PTM_inv


# ----------------------------------------------------------------------
# 3. Decomopose into the weighted difference of CPTP maps
# ----------------------------------------------------------------------


def get_CP_Choi(choi):
    """Decompose the Choi matrix into the difference of two CP maps.
    See Eq. (15) in Rossini2023."""

    eigv, eigs = np.linalg.eig(choi.full())
    projectors = [np.outer(v, v.conj()) for v in eigs.T]
    choi_plus = sum(max(0, ev.real) * P for ev, P in zip(eigv, projectors))
    choi_minus = sum(max(0, -ev.real) * P for ev, P in zip(eigv, projectors))

    # add offset for numerical stability
    if np.sum(np.abs(choi_minus)) != 0:
        reg = offset * sum(projectors)
        choi_plus += reg
        choi_minus += reg

    return q.Qobj(choi_plus), q.Qobj(choi_minus)


def get_p(choi_minus):
    """Find the p value.
    See Eq. (12) in Rossini2023."""

    kraus_sum = choi_minus[0::2, 0::2] + choi_minus[1::2, 1::2] # careful: ::, not :
    eigv, _ = np.linalg.eig(kraus_sum)
    return max(eigv + offset).real, kraus_sum


def get_Choi_D(choi_minus):
    """Construct the D matrix to make the Choi matrices TP.
    See Eq. (13) in Rossini2023."""

    p, kraus_sum = get_p(choi_minus)
    if is_trace_preserving(choi_minus / p):
        if verbose:
            print("Info: choi_minus/p is TP, so we choose the zero matrix for D.")
            print("---------------------------------------")
        return p, q.Qobj(np.zeros((4, 4)))

    # Check if kraus_sum can have off-diagonal elements (I assume this is the case)
    # If kraus_sum is diagonal, the STM_D contains the difference of the kraus_sum diagonal entries in the top left or bottom right corner.
    if verbose:
        is_diagonal = np.allclose(kraus_sum[0, 1] + kraus_sum[1, 0], 0, atol=1e-3)
        print("kraus_sum is diagonal", is_diagonal)

    D_dag_D = p * np.eye(2) - kraus_sum
    D = q.Qobj(la.sqrtm(D_dag_D))
    STM_D = Kraus_to_STM([D])
    choi_D = STM_to_Choi(STM_D)
    return p, choi_D


def get_CPTP_Choi(choi):
    choi_plus, choi_minus = get_CP_Choi(choi)
    p, choi_D = get_Choi_D(choi_minus)

    choi_plus = (choi_plus + choi_D) / (1 + p)
    choi_minus = (choi_minus + choi_D) / p

    return p, choi_plus, choi_minus

# ----------------------------------------------------------------------
