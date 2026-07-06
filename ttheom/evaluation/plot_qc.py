import matplotlib.pyplot as plt

def plotQC(**kwargs):
    """Plot the quantum circuit from the provided keyword arguments."""
    qc = kwargs.get("qc")
    if qc is None:
        raise ValueError("Quantum circuit (qc) must be provided in kwargs.")
    
    fig, ax = plt.subplots()
    ax.axis('off')
    # ax.set_title("Quantum Circuit")
    
    qc.draw("mpl", ax=ax)
    
    return fig, ax