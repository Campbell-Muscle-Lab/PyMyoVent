import numpy as np
import pandas as pd
from scipy.signal import butter, lfilter, freqz, filtfilt
from matplotlib import pyplot as plt


def butter_lowpass(self,cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a


def lowpass_filter(self,data):
    # Filter requirements.
    order = 6
    fs = 200       # sample rate, Hz
    cutoff = 10#3.667  # desired cutoff frequency of the filter, Hz
    b, a = butter_lowpass(self,cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y

def moving_average(self,data):
    MA=data.rolling(windoe=100).mean()
    return MA


# Get the filter coefficients so we can check its frequency response.
"""b, a = butter_lowpass(cutoff, fs, order)

# Plot the frequency response.
w, h = freqz(b, a, worN=8000)
plt.subplot(2, 1, 1)
plt.plot(0.5*fs*w/np.pi, np.abs(h), 'b')
plt.plot(cutoff, 0.5*np.sqrt(2), 'ko')
plt.axvline(cutoff, color='k')
plt.xlim(0, 0.5*fs)
plt.title("Lowpass Filter Frequency Response")
plt.xlabel('Frequency [Hz]')
plt.grid()"""


# Demonstrate the use of the filter.
# First make some data to be filtered.
"""T = 5.0             # seconds
n = int(T * fs)     # total number of samples
t = np.linspace(0, T, n, endpoint=False)
# "Noisy" data.  We want to recover the 1.2 Hz signal from this.
data = np.sin(1.2*2*np.pi*t) + 1.5*np.cos(9*2*np.pi*t) \
        + 0.5*np.sin(12.0*2*np.pi*t)

# Filter the data, and plot both the original and filtered signals.
y = lowpass_filter(data, cutoff, fs, order)

plt.subplot(2, 1, 2)
plt.plot(t, data, 'b-', label='data')
plt.plot(t, y, 'g-', linewidth=2, label='filtered data')
plt.xlabel('Time [sec]')
plt.grid()
plt.legend()

plt.subplots_adjust(hspace=0.35)
plt.show()"""
