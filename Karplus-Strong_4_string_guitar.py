# -*- coding: utf-8 -*-
"""
Created on Wed May 06 00:12:22 2020

@author: Harshil
"""

import pyaudio
import numpy as np
import wave

WIDTH = 2
CHANNELS = 2
RATE = 44100

p = pyaudio.PyAudio()

number_of_strings = 4
# initialize plunk to false
flag_punk = [False, False, False, False]
# initialise buffer of different size for different string tone
buffer_ks_size = [200, 210, 220, 230]

buffer_ks = []
for string in range(number_of_strings):
    buffer_ks.append(np.zeros(buffer_ks_size[string], dtype=np.float32))

# initialize array with plunk random numbers
buffers_ks_plunk = []
for string in range(number_of_strings):
    buffers_ks_plunk.append(np.random.uniform(-1, 1, buffer_ks_size[string]))

# pointer to karplus_strong 4 buffer
ptr_out = [1, 1, 1, 1]
ptr_in = [0, 0, 0, 0]

# Decaying factor: 0 < factor <= 0.5
factor = 0.499

def plunk_string(string_number):
    global buffer_ks, buffer_ks_plunk
    buffer_ks[string_number] = np.copy(buffer_ks_plunk[string_number])

def copy_buffer_ks_to_buffer_output(result, frame_count):
    global buffer_ks, ptr_in, ptr_out, number_of_strings
    for i in range(frame_count):
        # left channel
        result[i, 0] = 0.0
        for string in range(number_of_strings):
            result[i, 0] += buffer_ks[string][ptr_in[string]]
        result[i, 0] /= number_of_strings

        # right channel 
        result[i, 1] = result[i, 0]
        for string in range(number_of_strings):
            buffer_ks[string][ptr_in[string]] = factor * (buffer_ks[string][ptr_in[string]] + buffer_ks[string][ptr_out[string]])
        
        # update global pointer of buffer
        for string in range(number_of_strings):
            if ptr_in[string] < buffer_ks_size[string] - 1:
                ptr_in[string] += 1
            else:
                ptr_in[string] = 0
            if ptr_out[string] < buffer_ks_size[string] - 1:
                ptr_out[string] = 0
            else:
                ptr_out[string] = 0
        
    return result
    
frame_count_global = 0
frames_to_file = []
result = np.zeros((1024, 2), dtype=np.float32)

chunk_length = 0