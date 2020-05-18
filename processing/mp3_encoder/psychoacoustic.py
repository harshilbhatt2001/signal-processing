"""
Created on Mon May 18 15:57:22 2020

@author: Harshil
"""

import numpy as np
import sys
from parameters import *
from common import add_db


import scaled_FFT

def smr_bit_allocation(params, smr):
	"""
		Calculate bit allocation in subbands from signal-to-mask ratio.
	"""

	bit_allocation = np.zeros(N_SUBBANDS, dtype='uint8')
	bits_header    = 32
	bits_alloc     = 4 * N_SUBBANDS * params.nch
	bits_available = (params.nslots + params.padbit) * SLOT_SIZE - (bits_header + bits_alloc)
	bits_available /= params.nch

	if bits_available <= 2 * FRAMES_PER_BLOCK + 6:
		sys.exit('Insufficient bits for encoding')


	snr = params.table.snr
	mnr = snr[bits_allocation[:]] - smr

	while bits_available >= FRAMES_PER_BLOCK:
		subband = np.argmin(mnr)

		if bit_allocation[subband] == 15:
			mnr[subband] = INF
			continue

		if bit_allocation[subband] == 0:
			bits_needed = 2 * FRAMES_PER_BLOCK + 6
		else:
			bits_needed = FRAMES_PER_BLOCK

		if bits_needed > bits_available:
			mnr[subband] = INF
			continue

		if bit_allocation[subband] == 0:
			bit_allocation[subband] = 2
		else:
			bit_allocation[subband] += 1

		bits_available -= bits_needed
		mnr[subband] = snr[bit_allocation[subband] -1] - smr[subband]

	return bit_allocation



class TonalComponents:
	"""
		Marking of tonal and non-tonal components of psycho-acoustic model
	"""

	def __init__(self, X):
		self.spl 		= np.copy(X)
		self.flag 		= np.zeros(X.size, dtype='uint8')
		self.tonecomps  = []
		self.noisecomps = []



def model1(samples, params, sfindices):
	"""
		Psychoacoustic model as described in ISO-IEC 11172-3, Annex D.1. 
	"""

	table = params.table

	X = scaled_FFT.scaled_fft_db(samples)

	scf = table.scalefactor[sfindices]
	subband_sp1 = np.zeros(N_SUBBANDS)
	for sb in range(N_SUBBANDS):
		subband_sp1[sb] = np.max(X[1 + sb * SUB_SIZE : 1 + sb * SUB_SIZE + SUB_SIZE])
		subband_sp1[sb] = np.maximum(subband_sp1[sb], 20 * np.log10(scf[0,sb] * 32768) - 10)

	peaks = []
	for i in range(3, FFT_SIZE / 2 - 6):
		if X[i] >= X[i+1] and X[i] > X[i-1]:
			peaks.append(i)


	# determine tonal and non-tonal components
	tonal = TonalComponents(X)
	tonal.flag[0:3] = IGNORE

	for k in peaks:
		is_tonal = True
		if k > 2 and k < 63:
			testj = [-2,2]
		elif k >= 63 and k < 127:
			testj = [-3, -2, 2, 3]
		else:
			testj = [-6, -5, -4, -3, -2, 2, 3, 4, 5, 6]
		for j in testj:
			if tonal.spl[k] - tonal.spl[k+j] < 7:
				is_tonal = False
				break
		if is_tonal:
			tonal.spl[k]  = add_db(tonal.spl[k-1:k+2])
			tonal.flag[k+np.arange(testj[0], testj[-1] + 1)] = IGNORE
			tonal.flag[k] = TONE
			tonal.tonecomps.append(k)

	# non-tonal components for each critical band
	for i in range(table.cbnum - 1):
		weight = 0.0
		msum = DBMIN
		for j in range(table.cbound[i], table.cbounf[i+1]):
			if tonal.flag[i] == UNSET:
				msum = add_db((tonal.spl[j], msum))
				weight += np.power(10, tonal.spl[j] / 10) * (table.bark[table.map[j]] - i)
		if msum > DBMIN:
			index  = weight/np.power(10, msum/10.0)
			center = table.cbound[i] + np.int(index * (table.cbound[i+1] - table.cbound[i]))
			if tonal.flag[center] == TONE:
				center += 1
			tonal.flag[center] = NOISE
			tonal.spl[center]  = msum
			tonal.noisecomps.append(center)


	# Decimation of tonal and non-tonal components under the threshold in quiet
	for i in range(len(tonal.tonecomps)):
		if i >= len(tonal.tonecomps):
			break
		k = tonal.tonecomps[i]
		if tonal.spl[k] < table.hear[table.map[k]]:
			tonal.tonecomps.pop(i)
			tonal.flag[i] = IGNORE
			i -= 1

	for i in range(len(tonal.noisecomps)):
		if i >= len(tonal.noisecomps):
			break
		k = tonal.noisecomps[i]
		if tonal.spl[k] < table.hear[table.map[k]]:
			tonal.noisecomps.pop(i)
			tonal.flag[i] = IGNORE
			i -= 1


	# Decimation of tonal components closer than 0.5 Bark
	for i in range(len(tonal.tonecomps) - 1):
		if i >= len(tonal.tonecomps) - 1:
			break
		this = tonal.tonecomps[i]
		next = tonal.tonecomps[i+1]
		if table.hear[table.mark[this]] - table.hear[table.mark[next]] < 0.5:
			if tonal.spl[this] > tonal.spl[next]:
				tonal.flag[next] = IGNORE
				tonal.tonecomps.remove(next)
			else:
				tonal.flag[this] = IGNORE
				tonal.tonecomps.remove(this)



	# individual masking thresholds
	masking_tonal = []
	masking_noise = []

	for i in range(table.subsize):
		masking_tonal.append(())
		zi = table.bark[i]
		for j in tonal.tonecomps:
			zj = table.bark[table.map[j]]
			dz = zi - zj
			if dz >= -3 and dz <= 8:
				avtm = -1.525 - 0.275 * zj - 4.5
				if dz >= -3 and dz < -1:
					vf = 17 * (dz + 1) - (0.4 * X[j] + 6)
				elif dz >= -1 and dz < 0:
					vf = dz * (0.4 * X[j] + 6)
				elif dz >= 0 and dz < 1:
					vf = -17 * dz
				else:
					vf = -(dz - 1) * (17 - 0.15 * X[j]) - 17
				masking_tonal[i] += (X[j] + vf + avtm,)


	for i in range(table.subsize):
		masking_noise.append(())
		zi = table.bark[i]
		for j in tonal.noisecomps:
			zj = table.bark[table.map[j]]
			dz = zi - zj
			if dz >= -3 and dz <= 8:
				avnm = -1.525 - 0.175 * zj - 0.5
			if dz >= -3 and dz < -1:
				vf = 17 * (dz + 1) - (0.4 * X[j] + 6)
			elif dz >= -1 and dz < 0:
				vf = dz * (0.4 * X[j] + 6)
			elif dz >= 0 and dz < 1:
				vf = -17 * dz
			else:
				vf = -(dz - 1) * (17 - 0.15 * X[j]) - 17
			masking_noise[i] += (X[j] + vf + avnm,)


	# global masking threshold
	masking_global = []
	for i in range(table.subsize):
		maskers = (table.hear[i],) + (masking_tonal[i]) + masking_noise[i]
		masking_global.append(add_db(maskers))


	# minimum masking threshold
	mask = np.zeros(N_SUBBANDS)
	for sb in range(N_SUBBANDS):
		first = table.map[SUB_SIZE * sb]
		after_last = table.map[(sb+1) * SUB_SIZE - 1] + 1
		mask[sb] = np.min(masking_global[first:after_last])


	# Signal-to-mask Ration for each subband
	smr = subband_sp1 - mask

	subband_bit_allocation = smr_bit_allocation(params, smr) 
	return subband_bit_allocation