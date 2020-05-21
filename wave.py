import scipy.io.wavfile as wavfile
import scipy
import scipy.fftpack as fftpk
import numpy as np
from matplotlib import pyplot as plt

s_rate, signal = wavfile.read("wave.wav") 

FFT = abs(scipy.fft(signal))
freqs = fftpk.fftfreq(len(FFT), (1.0/s_rate))


plt.plot(freqs[range(len(FFT)//2)], FFT[range(len(FFT)//2)])                                                          
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.show()

