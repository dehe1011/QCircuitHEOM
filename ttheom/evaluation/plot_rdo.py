import numpy as np
import matplotlib.pyplot as plt

def plotRDO(t_list, rdo_list, **kwargs):
    """Plot the elements of a list of density matrices over time."""

    omegaQ = 2*np.pi*np.array(kwargs['freqQ'])
    omegaQmax = max(omegaQ)
    t = t_list / omegaQmax

    dm_list = rdo_list
    dim = dm_list[0].shape[0]
    fig, axes = plt.subplots(
        dim, dim, figsize=(max(dim * 2.2, 5), max(dim * 1.4, 4)),
        sharex=True, sharey=True, tight_layout=True,
    )
    if dim == 1:
        axes = np.array([[axes]])

    for i in range(dim):
        for j in range(dim):
            ax = axes[i, j]
            re  = [rho[i, j].real for rho in dm_list]
            im  = [rho[i, j].imag for rho in dm_list]
            ab  = [abs(rho[i, j])  for rho in dm_list]
            ax.plot(t, re, linewidth=1.5, label="Re")
            ax.plot(t, im, linewidth=1.5, label="Im")
            ax.plot(t, ab, linewidth=1.5, linestyle="--", label="Abs.")
            ax.set_yticks([-1, 0, 1])
            ax.tick_params(labelsize=7)

    for j in range(dim):
        axes[-1, j].set_xlabel("t [ns]", fontsize=8)
    axes[0, 0].legend(loc="upper right", fontsize=6)
    return fig, axes