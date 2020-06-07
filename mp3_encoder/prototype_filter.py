'''
Created on Fri May 15 23:28:22 2020

@author: Harshil Bhatt
'''


import scipy.signal as sp
import numpy as np

def prototype_filter():
    """ 

        Compute the prototype filter used in subband coding. The filter
        is a 512-point lowpass FIR h[n] with bandwidth pi/64 and stopband
        starting at pi/32

    """

    M = 512             # number of taps
    Fs = np.pi          # sampling rate
    Fpass = np.pi/128   # passband edge
    Fstop = np.pi/32    # stopband edge

    h = sp.remez(M, [0, Fpass/2, Fstop/2, Fs/2], [2,0], fs=Fs)
    return h
