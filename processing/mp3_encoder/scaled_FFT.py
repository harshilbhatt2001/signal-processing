"""
Created on Thu May 14 16:34:22 2020

@author: Harshil
"""


import numpy as np

def scaled_fft_db(x):
    """ ASSIGNMENT 1:
        a) Compute a 512-point Hann window and use it to weigh the input data.
        b) Compute the DFT of the weighed input, take the magnitude in dBs and
        normalize so that the maximum value is 96dB.
        c) Return the first 257 values of the normalized spectrum
        Arguments:
        x: 512-point input buffer.
        Returns:
        first 257 points of the normalized spectrum, in dBs
    """

    N = len(x)                                                  # Length of window
    n = np.arange(N)

    # Compute constant c for Hann Window
    w_cos = np.cos((2 * np.pi * n)/(N-1))
    sum_sq = np.sum((w_cos/2)**2)
    c = np.sqrt((N-1)/sum_sq)

    # Apply Hanning window
    x = x * c/2 * (1 - np.cos(2 * np.pi * n/(N-1)))

    # Compute the fft of x, normalized by the size of the input
    X = np.fft.rfft(x)/N

    # Keep only first N/2 + 1 samples of fft
    X = X[0:int(N/2 + 1)]

    # Take the magnitude of X
    X_mag = np.abs(X)
    nonzero_magX = np.where(X_mag != 0)[0]

    # Convert the magnitudes to dB
    X_db = -100 * np.ones_like(X_mag)                           # Set the default dB to -100
    X_db[nonzero_magX] = 20*np.log10(X_mag[nonzero_magX])       # Compute the dB for nonzero magnitude indices

    # Rescale to amx of 96 dB
    max_db = np.amax(X_db)
    X_db = 96 - max_db + X_db

    return X_db

