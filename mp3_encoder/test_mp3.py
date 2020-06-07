"""
Created on Thu May 14 20:27:22 2020

@author: Harshil
"""

import numpy as np
from scipy.io import wavfile

try:
    from scaled_FFT import *
except:
    print("scaled_FFT files not found")
try:
    from prototype_filter import *
except:
    print("prototype_filter files not found")



def check_scaled_FFT():

    pass_test = True

    for i in range(1,5):
        print('\nTest %d:' % (i))
        fin = 'data/testInput' + str(i) + '.wav'
        fout = 'data/testOutput' + str(i) + '.wav'

        r,x = wavfile.read(fin)

        # compute output of assignment function
        X = scaled_fft_db(x)

        if X.shape[0] == 257:
            print('Signal size is 257:\t\tPASS')
        else:
            print('Signal size is 257:\t\tFAIL')
            pass_test = pass_test and False

        if np.abs(X.max() - 96) < 1e-5:
            print('Maximum is 96 dB:\t\tPASS')
        else:
            print('Maximum is 96 dB:\t\tFAIL')
            pass_test = pass_test and False

        # compare to test output file content
        X_check = np.loadtxt(fout)

        if np.allclose(X, X_check,atol=1e-1):
            print('Test signals output match:\tPASS')
        else:
            print('Test signals output match:\tFAIL')
            pass_test = pass_test and False

    x = np.ones(512)
    x[1:-1] = 1./np.hanning(512)[1:-1]
    X = scaled_fft_db(x)
    win_test = np.zeros(257)
    win_test[0] = 96

    if X[0] == 96 and np.all(X[1:] < 50):
        print('Test hanning window:\tPASS')
    else:
        print('Test hanning window:\tFAIL')
        pass_test = pass_test and False

    if pass_test:
        print('\nCongratulations, your algorithm passed all the tests.')
    else:
        print('Sorry, your algorithm did not pass all tests.')
    

def check_prototype_filter(plot=False):

    from parameters import filter_coeffs

    h = prototype_filter()

    # Create the cosine filter bank
    cosine_bank = np.cos(np.pi/64. * (2*np.arange(32)[:, np.newaxis]+1)*(np.arange(h.shape[0])-16))
    fb = cosine_bank*h

    # Frequency response
    from numpy import fft
    f = np.arange(257)/256./2.
    H = fft.fft(h)[:257]
    FB = fft.fft(fb, axis=1)[:, :257].T

    # ideal filter template
    ideal = np.zeros(257)
    f_pass = 1./256. # pass band is set according to standard
    f_stop = 1./64.  # stop band
    Ilo = f <= f_pass
    Ihi = f >= f_stop
    I_both = np.logical_or(Ilo, Ihi)
    ideal[f < f_stop] = 0.5
    ideal[f <= f_pass] = 2.

    if plot:
        # plot prototype filter and constraints
        import matplotlib.pyplot as plt
        plt.subplot(2,1,1)
        plt.plot(f, np.abs(H))
        plt.plot(f[I_both], ideal[I_both], 'o')

        plt.legend(('prototype filter','constraints'))
        plt.title('Prototype Filter')
        plt.xlabel('Normalized frequency')
        plt.ylabel('Magnitude')

        err_hi = np.sqrt(np.sum(np.abs(np.abs(H[Ihi])-ideal[Ihi])**2))
        if (err_hi < 1e-2):
            plt.xlim((0.,2*f_stop))

        # plot the filter bank and the sum response
        plt.subplot(2,1,2)
        plt.plot(f, np.abs(FB))
        plt.plot(f, np.abs(np.sum(FB, axis=1)))
        plt.title('Filter Bank')
        plt.xlabel('Normalized frequency')
        plt.ylabel('Magnitude')

        plt.show()

    # compute the error only on pass band and stop
    # band, not the transition band.
    error = np.abs(ideal[I_both]-np.abs(H[I_both]))

    if error.max() < 0.05:
        print('Congratulations, the filter seems to satisfy the design constraints.')
    else:
        print('The filter fails to satisfy the constraints.')





if __name__ == "__main__":
    check_scaled_FFT()
    check_prototype_filter(plot=True)
