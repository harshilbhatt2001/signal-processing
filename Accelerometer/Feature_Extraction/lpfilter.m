function Hd = lpfilter
%LPFILTER Returns a discrete-time filter object.

% MATLAB Code
% Generated by MATLAB(R) 9.8 and Signal Processing Toolbox 8.4.
% Generated on: 08-Jun-2020 18:06:46

% Chebyshev Type I Lowpass filter designed using FDESIGN.LOWPASS.

% All frequency values are in Hz.
Fs = 198;  % Sampling Frequency

N     = 20;  % Order
Fpass = 20;  % Passband Frequency
Apass = 1;   % Passband Ripple (dB)

% Construct an FDESIGN object and call its CHEBY1 method.
h  = fdesign.lowpass('N,Fp,Ap', N, Fpass, Apass, Fs);
Hd = design(h, 'cheby1');

% [EOF]
