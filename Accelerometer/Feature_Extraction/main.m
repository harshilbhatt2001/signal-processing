clear 
clc
data = readtable('Data\Raw_Data2.csv');

%%

fs = 1/ 0.005037;
hpf = hpfilter;
lpf = lpfilter;

%%
filtered_x_hp = filter(hpf, data.AccelerationX_m_s_2_);
filtered_x_lp = filter(lpf, filtered_x_hp);


filtered_abs_hp = filter(hpf, data.AbsoluteAcceleration_m_s_2_);
filtered_abs_lp = filter(lpf, filtered_abs_hp);
%filtfilt_x = filtfilt(lpf, filtered_x_lp)

%%
figure
hold on
plot(data.Time_s_, data.AbsoluteAcceleration_m_s_2_, 'b')
plot(data.Time_s_, filtered_abs_hp, 'r')
hold off
%plot(data.Time_s_, filtered_abs_lp, 'k')
%plot(data.Time_s_, filtfilt_x, 'bl')

%%
%Select walking section from 17s to 27s
walking_abs = filtered_abs_hp(3400:5400, 1);
[p, f] = pwelch(walking_abs, [], [], [], fs);

fmindist = 0.25;                    % Minimum distance in Hz
N = 2*(length(f)-1);                % Number of FFT points
minpkdist = floor(fmindist/(fs/N)); % Minimum number of frequency bins

[pks,locs] = findpeaks(p,'npeaks',8,'minpeakdistance',minpkdist,...
    'minpeakprominence', 0.15);

% Plot PSD and overlay peaks
figure
plot(f,db(p),'.-')
grid on
hold on
plot(f(locs),db(pks),'rs')
hold off
title('Power Spectral Density with Peaks Estimates')
xlabel('Frequency (Hz)')
ylabel('Power/Frequency (dB/Hz)')

