"""
Created on Thu May 14 16:34:22 2020

@author: Harshil
"""


import numpy as np
from numpy.fft import fft, ifft, rfft

def scaled_fft_db(x):
    """ ASSIGNMENT 1

        Computes the FFT of the input buffer windowed by a Hann window, scales
        the output so that the maximum is at 96 dB. The output should be in
        decibels.

        Arguments:
        x: Input buffer.

        Returns:
        X: The FFT of x (windowed by Hanning window) in dB, scaled to have maximum at 96 dB.
    """

    N = len(x)                                                  # Length of window
    n = np.arange(N)

    # Compute constant c for Hann Window
    w_cos = np.cos((2 * np.pi * n)/(N-1))
    sum_sq = np.sum((w_cos/2)**2)
    c = np.sqrt((N-1)/sum_sq)

    # Apply Hanning window
    x = x * c/2 * (1 - np.cos(2 * np.pi * n/(N-1)))

    # Compute fft of x, normalize by N
    X = rfft(x)/N

    # Keep only first N/2 + 1 samples of fft
    X = X[0:int(N/2 + 1)]

    X_mag = np.abs(X)
    nonzero_magX = np.where(X_mag != 0)[0]

    # Convert mag to dB
    X_db = -100 * np.ones_like(X_mag)                           # Set default dB to -100
    X_db[nonzero_magX] = -20 * np.log10(X_mag[nonzero_magX])    # Compute dB for non-zero magnitude 

    # Rescale to max of 96dB
    max_db = np.amax(X_db)
    X_db = 96 - max_db + X_db

    return X_db

