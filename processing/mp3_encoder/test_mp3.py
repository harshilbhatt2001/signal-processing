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


if __name__ == "__main__":
    check_scaled_FFT()