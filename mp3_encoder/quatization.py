"""
Created on Tue May 19 00:57:22 2020

@author: Harshil
"""


import numpy as np

def quantization(sample, sf, ba, QCa, QCb):
    """ 
        Arguments:
        sample: the sample to quantize
        sf:     the scale factor
        ba:     the bit allocation
        QCa:    the multiplicative uniform quantization parameter
        QCb:    the additive uniform quantization parameter

        Returns:
        The uniformly quantized sample.
    """

    return np.floor((QCa*sample/sf + QCb)*2**(ba-1))