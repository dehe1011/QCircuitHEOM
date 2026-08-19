import os
import numpy as np
import pandas as pd

def loadCSV(csvFilePath):
    """Load timesteps and density matrices from a CSV file.

    Parameters
    ----------
    csvFilePath : str
        Path to the CSV file. The first column is time; the remaining columns
        hold real and imaginary parts of the density-matrix entries in
        row-major order (alternating real, imaginary).

    Returns
    -------
    times : numpy.ndarray
        1-D array of time points.
    rhos : list of numpy.ndarray
        List of density matrices, one per time step.
    """
    df = pd.read_csv(csvFilePath, header=None)
    times = df.iloc[:, 0].to_numpy()
    data = df.iloc[:, 1:].to_numpy()

    # Each complex number is two columns: (Re, Im)
    n_entries = data.shape[1] // 2
    dim = int(np.sqrt(n_entries))

    rhos = []
    for row in data:
        complex_entries = row[0::2] + 1j * row[1::2]
        rho = complex_entries.reshape((dim, dim))
        rhos.append(rho)

    return times, rhos

def getResult(directory, fileName):
    """Load simulation results from a saved CSV file.

    Parameters
    ----------
    directory : str
        Directory containing the CSV file.
    fileName : str
        Base name of the file (without extension).

    Returns
    -------
    results : numpy.ndarray
        Array of shape ``(numSteps, 2**numQ, 2**numQ)`` containing the reduced
        density matrices at each time step.
    """
    csvFilePath = os.path.join(os.getcwd(), directory, fileName + '.csv')
    t_list, rdo_list = loadCSV(csvFilePath)
    return t_list, rdo_list