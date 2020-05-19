"""
Created on Tue May 19 01:47:22 2020

@author: Harshil
"""


import sys
import os.path
import numpy as np
import psychoacoustic as psycho
from common import *
from parameters import *
from prototype_filter import *
from subband_filtering import *
from quatization import *



def main(inwavfile, outmp3file, bitrate):
	"""ENCODER MAIN FUNCTION"""

	# Read WAVE file and set MPEG encoder parameters
	input_buffer = WavRead(inwavfile)
	params = EncoderParameters(input_buffer.fs, input_buffer.nch, bitrate)


	# Read baseband filter samples
	baseband_filter = prototype_filter().astype=('float32')

	subband_samples = np.zeros((params.nch, N_SUBBANDS, FRAMES_PER_BLOCK), dtype='float32')

	# Main loop executing until all samples have been processed
	while input_buffer.nprocessed_samples < input_buffer.nsamples:

		# In each block 12 frames are processed, which equals 12x32=384 samples per block
		for frm in range(FRAMES_PER_BLOCK):
			samples_read = input_buffer.read_sample(SHIFT_SIZE)

			# Perform zero padding if all samples have been read
			if samples_read < SHIFT_SIZE:
				input_buffer.audio[ch].insert(np.zeros(SHIFT_SIZE - samples_read))


		# Filtering = dot product with reverse buffer
		for ch in range(params.nch):
			subband_samples[ch,:,frm] = subband_filtering(input_buffer.audio[ch].reversed(), baseband_filter)


		# Declaring arrays for keeping table indices of calculated scalefactors and bits allocated in subbands.
		# Number of bits allocated in subband is either 0 or in range [2,15]
		sfcindices = np.zeros((params.nch, N_SUBBANDS), dtype='uint8')
		subband_bit_allocation = np.zeros((params.nch, N_SUBBANDS), dtype='uint8')
		smr = np.zeros((params.nch, N_SUBBANDS), dtype='float32')


		# Finding scale factors, psychoacoustic model and bit allocation calculation for subbands. Although scaling is done later, 
		# its result is necessary for the psychoacoustic model and calculation of  sound pressure levels.
		for ch in range(params.nch):
			sfcindices[ch,:] = get_scalefactors(subband_samples[ch,:,:], params.table.scalefactor)
			subband_bit_allocation[ch,:] = psycho.model1(input_buffer.audio[ch].ordered(), params, sfindices)


		subband_samples_quantized = np.zeros(subband_samples.shape, dtype='uint32')
		for ch in range(params.nch):
			for sb in range(N_SUBBANDS):
				QCa = params.table.qca[subband_bit_allocation[ch,sb]-2]
				QCb = params.table.qcb[subband_bit_allocation[ch,sb]-2]
				scf = params.table.scalefactor[sfcindices[ch,sb]]
				ba  = subband_bit_allocation[ch, sb]
				for ind in (FRAMES_PER_BLOCK):
					subband_samples_quantized[ch,sb,ind] = quantization(subband_samples[ch,sb,ind], scf, ba, QCa, QCb)


		# Fromatting output bitstream and appending it to the output file
		bitstream_formatting(outmp3file,
							 params, 
							 subband_bit_allocation, 
							 sfcindices, 
							 subband_samples_quantized)



if __name__ == "__main__":
	if len(sys.argv) < 3:
		sys.exit('Please provide input WAVE file and desired bitrate')
	inwavfile = sys.argv[1]
	if len(sys.argv) == 4:
		outmp3file = sys.argv[2]
		bitrate    = int(sys.argv[3])
	else:
		outmp3file = inwavfile[:-3] + 'mp3'
		bitrate    = int(sys.argv[2])

	if os.path.exists(outmp3file):
		sys.exit('Output file already exists')

	main(inwavfile, outmp3file, bitrate)
