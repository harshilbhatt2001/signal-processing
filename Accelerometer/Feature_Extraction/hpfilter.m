function Hd = hpfilter
%HPFILTER Returns a discrete-time filter object.

% MATLAB Code
% Generated by MATLAB(R) 9.8 and Signal Processing Toolbox 8.4.
% Generated on: 08-Jun-2020 17:51:54

% Chebyshev Type II Highpass filter designed using FDESIGN.HIGHPASS.

% All frequency values are in Hz.
Fs = 198.5309;  % Sampling Frequency

N     = 20;  % Order
Fstop = 10;   % Stopband Frequency
Astop = 80;  % Stopband Attenuation (dB)

% Construct an FDESIGN object and call its CHEBY2 method.
h  = fdesign.highpass('N,Fst,Ast', N, Fstop, Astop, Fs);
Hd = design(h, 'cheby2');

% [EOF]
