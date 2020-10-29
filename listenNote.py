import sys
from math import log2, pow
import collections

A4 = 440
C0 = A4*pow(2, -4.75)
name = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    
def getNote(freq):
    if freq == 0: return ''
    h = round(12*log2(freq/C0))
    octave = h // 12
    n = h % 12
    return name[n]


import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import peakutils

np.set_printoptions(suppress=True) # don't use scientific notation

CHUNK = 2**15 # number of data points to read at a time
RATE = 48000 # time resolution of the recording device (Hz)

p=pyaudio.PyAudio() # start the PyAudio class
stream=p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True,
            frames_per_buffer=CHUNK) #uses default input device


kill=False

def waitToPlay(notes):
    while not kill: 
        data = np.frombuffer(stream.read(CHUNK),dtype=np.int16)
        #data = data[1::2] #chooses only channel 1(counted from 0)
        vol=np.average(np.abs(data))*2
        data = data * np.hanning(len(data)) # smooth the FFT by windowing data
        fft = abs(np.fft.fft(data).real)
        fft = fft[:int(len(fft)/2)] # keep only first half
        freq = np.fft.fftfreq(CHUNK,1.0/RATE)
        freq = freq[:int(len(freq)/2)] # keep only first half

        peakInds = peakutils.indexes(fft, thres=0.2, min_dist=1)
        peaksNotes = [getNote(freq[v]) for v in peakInds]
        #peaksNotes = [getNote(freq[v]) for v in np.where(fft>np.average(fft)*400)[0]]
        foundNotes = []

        for note in collections.Counter(peaksNotes).most_common(len(notes)):
            foundNotes.append(note[0])

        print(foundNotes, vol)

        if vol > 2 and notes == set(foundNotes) :
            break

def end():
    stream.stop_stream()
    stream.close()

    p.terminate()
    
    kill=True