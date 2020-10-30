import sys
import time
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

#RATE = 48000 # time resolution of the recording device (Hz)
#CHUNK = 2**10 # number of data points to read at a time
#CHUNK_NUM = 32

p=pyaudio.PyAudio() # start the PyAudio class

kill=False

def soundAnalyzer(input, output):
    RATE = input['rate']
    CHUNK = input['chunk']
    CHUNK_NUM = input['chunk_num']

    stream=p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True,
                frames_per_buffer=CHUNK) #uses default input device

    data = np.frombuffer(stream.read(CHUNK),dtype=np.int16)
    for i in range(CHUNK_NUM-1):
        chunk = np.frombuffer(stream.read(CHUNK),dtype=np.int16)
        data = np.concatenate((data, chunk))

    lastNotes = set()
    repeated = 0
    skipped = 0
    errored = 0

    volMult = 2**16

    while not input['kill']: 
        data = data[CHUNK:]
        chunk = np.frombuffer(stream.read(CHUNK),dtype=np.int16)
        data = np.concatenate((data, chunk))
        
        #data = data[1::2] #chooses only channel 1(counted from 0)
        vol = np.average(np.abs(data))
        volMult = min(volMult, 2**16 / vol)
        vol = vol*volMult/2**16
        dataTMP = data * np.hanning(len(data)) # smooth the FFT by windowing data
        fft = abs(np.fft.fft(dataTMP).real)
        fft = fft[:int(len(fft)/2)] # keep only first half
        freq = np.fft.fftfreq(CHUNK*CHUNK_NUM,1.0/RATE)
        freq = freq[:int(len(freq)/2)] # keep only first half

        peakInds = peakutils.indexes(fft, thres=0.2, min_dist=1)
        peaksNotes = [getNote(freq[v]) for v in peakInds]
        #peaksNotes = [getNote(freq[v]) for v in np.where(fft>np.average(fft)*400)[0]]
        foundNotes = []

        for note in collections.Counter(peaksNotes).most_common(input['notesNum']):
            foundNotes.append(note[0])

        foundNotes = set(foundNotes)

        output["volume"] = vol

        if lastNotes.issubset(foundNotes) or len(lastNotes.intersection(foundNotes)) + len(lastNotes.difference(foundNotes)) < input['notesNum']:
            lastNotes = lastNotes.union(foundNotes)
        

        if vol > input['threshold'] and foundNotes == lastNotes:
            repeated += 1
        else:
            if foundNotes.issubset(lastNotes) and skipped < input['acceptableSkip']:
                skipped += 1
                repeated += 1
            else:
                if errored < input['acceptableError']:
                    errored += 1
                else:
                    lastNotes = foundNotes
                    repeated = 0
                    skipped = 0
        

        if input['freeze'] or vol < input['threshold']:
            repeated = 0

        output['repeated'] = repeated
        
        if vol > input['threshold']:
            print(repeated, foundNotes)
        
        if repeated >= input['callsToFire']:
            print(foundNotes)
            output['fired'].append(lastNotes)

    stream.stop_stream()
    stream.close()