import matplotlib.pyplot as plt

def plotQC(**kwargs):
    """Plot the Qiskit quantum circuit stored in *kwargs*.

    Parameters
    ----------
    **kwargs
        Must contain ``"qc"`` (a :class:`qiskit.QuantumCircuit`).

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object.
    ax : matplotlib.axes.Axes
        The axes containing the circuit diagram.

    Raises
    ------
    ValueError
        If ``"qc"`` is not present in *kwargs*.
    """
    qc = kwargs.get("qc")
    if qc is None:
        raise ValueError("Quantum circuit (qc) must be provided in kwargs.")
    
    fig, ax = plt.subplots()
    ax.axis('off')
    # ax.set_title("Quantum Circuit")
    
    qc.draw("mpl", ax=ax)
    
    return fig, ax