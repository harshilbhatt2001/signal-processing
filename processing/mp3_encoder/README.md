# MP3 Encoder

# Encoding a file with the final MP3 encoder

To encode a WAVE file, run the program with the following command line arguments:
```
>> python encoder.py inwavfile.wav [outmp3file] bitrate

```
Supported bitrates are 64 kbps to 448 kbps in 32 kbps steps (e.g. 64, 128, 256,...), with lower bitrates indicating a higher the compression ratio (and therefore lower quality). If outmp3file is omitted, the same filename as input file is used, but with .mp3 extension. If there is an error reading the WAVE file, maybe its format is not supported by the WavRead class (currently only standard integer PCM WAVE files are supported).

Two sample WAVE input files are provided, sampled at 44100Hz: 'sine.wav' - a stereo composed of 440 and 880 Hz sine waves, and 'saxophone.wav'. Try for instance:

```
>> python encoder.py samples/sine.wav samples/sine.mp3 320
```



# Lossy Compresion Scheme

![lossy](https://github.com/harshilbhatt2001/signal-processing/blob/mp3_enc/processing/mp3_encoder/images/lossy_intro.JPG)
Goal: reduce number of bits to represent original signal $$x[n]$$

Lossy compression: $$x[n]    $ \neq $    y[n]$$

We need to put noise where it is not perceptible to the human ear

## Block Diagram MP# Encoding

![block_diag](https://github.com/harshilbhatt2001/signal-processing/blob/mp3_enc/processing/mp3_encoder/images/block_diag.JPG)

Input signal enters a bank of 32 paraller subband filters. There are 32 parallel filters that subdivide the input signal into 32 independent channels that span the full spectral range of the input. Each channel is the quantized, and the quantized sample are then formatted and encoded in a continuous bit stream.

The quantization scheme is clever because the number of bits allocated to each sub-band is dependent on the perceptual importance of each sub-band with respect to the overall quality of the audio wave-form. In other words, subbands that are deemed by the Psycho-Acoustic Model not to be important or difficult to be perceived are allocated very few or no bits at all. Whereas, the most perceptually relevant subbands are allocated the bulk of the entire Bit budget. The reason why we can say flee allocate different amounts of beats to the different subbands is to be found in the so-called masking effect of the human auditory system.

Masking in the human ear takes place within critical bands, and critical bands are portions of the spectrum that are treated by the ear as a single unit. Everything that happens within a critical band can now be further resolved by the ear. So two different frequencies taking place in the same critical band are perceived as a single tone. There are approximately 24 critical bands in the human ear. They get wider as we go up in frequency. They follow a logarithmic scale, which means that the resolution power of the ear is stronger at low frequencies, whereas at high frequencies were less discriminant. And therefore, when we quantize things across critical bands, we can probably fit more noise in the high frequencies that in low frequencies. The purpose of the psychoacoustic model is to compute the minimum number of bits that we need to use to quantize each of the 32 subband filter outputs, so that the perceptual distortion is as little as possible. Finally, we're given a non-uniformed bit allocation which will allocate fewer bits to the bands where the masking is strongest.

## Working of Psycho-Acoustic Model

* Use FFT to estimate the energy of the signal in each subband
* Distinguish between tonal (sinusoid-like) and non-tonal (noise-like) component
* Determine individual masking effect of tonal and non-tonal component in each critical band
* Determine the total masking effect by summing the individual contributions
* Map this total effect to the 32 subbands
* Determine bit allocation by allocating prioritarily bits to subbands with lowest signal-to-mask ratio

## Subband Filtering

![subband filtering image](https://github.com/harshilbhatt2001/signal-processing/blob/mp3_enc/processing/mp3_encoder/images/subband_filtering.JPG)

the input is split across a filter bank that contains 32 filters isolating different parts of the spectrum. These filters are implemented as 512 tap FIR's, and they're followed by 32 times down sampler to provide the independence of band samples. The filter prototype is a simple low pass with a cut off frequency of $$\frac{\pi}{64}$$ and a total bandwidth of $$\frac{\pi}{32}$$. The different sub bands are obtained by modulating the base filter with a cosine at multiples of $$\frac{\pi}{64}$$.

Each branch in the filter bank comprises an FIR filter of length 512 and a 32 time down sampler here. What this means of course is that 31 out of 32 output samples of this filter are discarded, and so this is of course a very wasteful implementation.

![optimized subband filtering image](https://github.com/harshilbhatt2001/signal-processing/blob/mp3_enc/processing/mp3_encoder/images/optimized_subband_filtering.JPG)


## Eficient Implementation

* We will use a length-512 circular buffer b[k]
* Step 1: Shift in 32 input audiosamples into the circular buffer, newest first
* Step 2: Compute r[k] = h[k]b[k]
* Step 3: Compute c[q] = ![c[q] img](https://github.com/harshilbhatt2001/signal-processing/blob/mp3_enc/processing/mp3_encoder/images/c%5Bq%5D.JPG)
* Step 4: Compute the subband outputs as ![si(m) img](https://github.com/harshilbhatt2001/signal-processing/blob/mp3_enc/processing/mp3_encoder/images/si%5Bm%5D.JPG)

## Quantization

MP3 uses uniform quantization of subband samples. And the number of bits per sample in each subband is determined by the psychoacoustic model.

There are 36 samples per band and per frame in the MP3 standard. And so Since all of the 36 samples is going to be quantized by the same quantizer, a rescaling is needed so that we're using the full range of the quantizer.

### Rescaling

* use full quantization range
* normalization requires transmission of 32 bit scale factor 
* 16 predefined scale factors, 4 bits overhead

The actual quantization is performed according to this formula where b is the number of bits as provided by the psychoacoustic model, and Qa and Qb functions of the number bits are parameters that are encoded inside the MP3 standard.

![quant img](https://github.com/harshilbhatt2001/signal-processing/blob/mp3_enc/processing/mp3_encoder/images/quant.JPG)
