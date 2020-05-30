'''
This script receives:
    
sampfreq, data = wavfile.read()
from scipy.io import wavfile

and returns onsets depending on what paremeters you set. 
Low and high pass filters-like included.
Included Transient Points.

To do:
    -Use right channel for control. 
    -Use bpm against samples or note onset for accuracy percentage
    -Compare different methods against each other to find differences and trends

https://docs.scipy.org/doc/scipy/reference/generated/scipy.fft.fft.html
https://www.w3resource.com/python-exercises/numpy/python-numpy-exercise-31.php

'''
import numpy as np
import scipy
import scipy.fftpack as fftpk
import matplotlib.pyplot as plt

class Audio():
    def __init__(self, audiofile):
        self.sampfreq = audiofile[0]
        self.data = audiofile[1]/65536 #16 bits
        try: # 1 channel only
            if len(self.data[0]) > 1: 
                self.data = [i[0] for i in self.data]
                print("2 channels detected. Using left side.")
        except:
            pass
        print("Audio file was read.")
        
    def GetNoteOnset(self, unit = 2048, chunk_size = 2048, threshold_ratio = 0.8, HPF = 20, LPF = 500):
        pitch_sustain, self.notes = -1, []
        pitch_start,note_on = 0,0
        threshold = Get_Threshold(self.data, chunk_size, threshold_ratio)
        for i in range(int(len(self.data)/unit)):
            start = unit*(i)
            end = unit*(i) + chunk_size
            pitch = ReadChunk(self.data[start:end], threshold, LPF, HPF, self.sampfreq)
            try:
                if pitch != -1 and pitch != pitch_sustain: #Note change
                    note_on = start
                    pitch_sustain = pitch
                    pitch_start = pitch
                elif pitch == -1 and pitch_sustain>-1:
                    note_release = start
                    self.notes.append([pitch_start, note_on, note_release])
                    pitch_sustain = pitch
            except:
                print("There was an error somewhere btw")
                
    def GetTransientPoints(self, x):
        self.tp = []
        for i in self.notes:
            start = i[1] - x
            end = i[2] + x
            noteSamples = self.data[start:end]
            
            top = np.amax(noteSamples)
            bot = np.amin(noteSamples)
            if top > abs(bot):
                point = top
            else:
                point = bot
            transientPoint = int(max(np.where(noteSamples == point))[0]) + start
            self.tp.append(transientPoint)
        
    def GetBPM(self, minBPM = 60, maxBPM = 200, kind = "mode"):
        x = [i[1] for i in self.notes]
        d = [x[i+1]-x[i] for i in range(len(x)) if i < len(x)-1]
        if kind == "mean":
            beat_s = mean(d)/self.sampfreq
        elif kind == "mode":
            beat_s = mode(d)/self.sampfreq
        elif kind == "median":
            beat_s = median(d)/self.sampfreq
        else:
            print("Error")
        bpm = 60/beat_s
        while bpm < minBPM or bpm > maxBPM:
            if bpm < minBPM:
                bpm = bpm*2
            elif bpm > maxBPM:
                bpm = bpm/2
        return bpm
        
    def GetBPM_TP(self, minBPM, maxBPM, kind):
        d = [self.tp[i+1]-self.tp[i] for i in range(len(self.tp)) if i < len(self.tp)-1]
        if kind == "mean":
            beat_s = mean(d)/self.sampfreq
        elif kind == "mode":
            beat_s = mode(d)/self.sampfreq
        elif kind == "median":
            beat_s = median(d)/self.sampfreq
        else:
            print("Error.")
        bpm = 60/beat_s
        while bpm < minBPM or bpm > maxBPM:
            if bpm < minBPM:
                bpm = bpm*2
            elif bpm > maxBPM:
                bpm = bpm/2
        return bpm
    
    def GetNotesFrequencies(self, gridSize, chunk_size, HPF, LPF):
        bpm = Audio.GetBPM(self)
        grid_chunk_size = (60/bpm)*self.sampfreq*gridSize
        spectrum = []

        for i in range(len(self.notes)):
            start = self.notes[i][1] #gets Note Onset
            end = int(self.notes[i][1] + chunk_size)
            note_chunk = self.data[start:end]
            
            FFT = abs(scipy.fft.fft(note_chunk))
            freqs = fftpk.fftfreq(len(FFT), (1.0/self.sampfreq))
            
            low_pass_filter = freqs[abs(freqs) < LPF]
            high_pass_filter = low_pass_filter[abs(low_pass_filter) > HPF]
            
            filtered = FFT[:len(high_pass_filter)]
            
            spectrum.append([high_pass_filter,filtered])
            
        return spectrum
    
    def PlotNoteOnset(self):
        self.y = [i[0] for i in self.notes]
        self.x = [i[1]/self.sampfreq for i in self.notes]
        self.l = [i[2]-i[1] for i in self.notes] 
        plt.xlabel("Time (s)")
        plt.ylabel("Frequency (Hz)")
        plt.scatter(self.x,self.y)
        plt.show()
    
    def PlotNotesSpectrum(self, spectrum):
        for i in spectrum:
            PlotFreqs(i[0],i[1], 0, 1000)
        
      
def GetTopFrequencies(spectrum, ratio):
    top = []
    for i in spectrum: #Get top frequencies
        index = np.where(i[1] > np.amax(i[1])*ratio)
        top.append(abs(i[0][index])) 
    return top
    
# For visualizing chunks
def PlotFreqs(x, y, l, r):    
    fig1,ax1 = plt.subplots(subplot_kw=dict())
    ax1.plot(x[range(len(y)//2)],y[range(len(y)//2)])
    ax1.set_xlim(left = l, right = r)

def ReadChunk(chunk, threshold, LPF, HPF, sampfreq):
    FFT = abs(scipy.fft.fft(chunk))
    freqs = fftpk.fftfreq(len(FFT), (1.0/sampfreq))
    
    #The term is not accurate to synthesis but its a similar idea
    low_pass_filter = freqs[abs(freqs) < LPF]
    high_pass_filter = low_pass_filter[abs(low_pass_filter) > HPF]
    
    filtered = FFT[:len(high_pass_filter)]

    if np.amax(filtered) > threshold:
        index = np.where(filtered == np.amax(filtered))
        frequency = abs(high_pass_filter[index])
        #PlotFreqs(freqs, FFT, 0, 1000)
    else:
        frequency = -1
    return frequency

def Get_Threshold(data, chunk_size, ratio):
        low, high = [],[]
        for i in range(int((len(data)/chunk_size))-1):
            start = chunk_size*(i)
            end = chunk_size*(i) + chunk_size
            chunk = data[start:end]
            
            FFT = abs(scipy.fft.fft(chunk))

            low.append(np.amin(abs(FFT)))
            high.append(np.amax(abs(FFT)))

        return (max(high) - min(low)) * ratio

def mode(List):  #most frequent
    return max(set(List), key = List.count) 
def mean(List): #average value
    return sum(List)/len(List)
def median(List): #middle of the list
    return sorted(List)[int(len(List)/2)]

