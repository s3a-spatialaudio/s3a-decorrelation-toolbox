#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 12:59:03 2019
Plotting_Toolbox
Speedy tools for visualising spectra etc.
@author: mike
"""

from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt

import librosa
import librosa.display

import scipy.io.wavfile
from scipy import signal



import sys
sys.path.append('/Users/mike/Documents/Code/PythonDecorrelationToolbox')



def sPlot (multiChannelAudio, LF = 20, HF = 20000, fs = 48000, nperseg=4096*16):
    multiChannelAudio = multiChannelAudio.reshape(multiChannelAudio.shape[0],-1)
    lowbin = int(LF/(fs/nperseg))
    highbin = int(HF/(fs/nperseg))
    
    numChans = multiChannelAudio.shape[1]
    
    plt.figure(figsize=(10, 4))
    for n in range(numChans):
        f, Pxx_den = signal.welch(multiChannelAudio[:,n], fs, nperseg=nperseg)
        plt.loglog (f[lowbin:highbin], Pxx_den[lowbin:highbin])
        
    plt.xlabel('frequency [Hz]')
    plt.ylabel('PSD [V**2/Hz]')
    plt.show()
    
def plot (*args):
    
    plt.figure(figsize=(10, 4))
    for x in args:
        plt.plot(x)
    plt.show()

def plotim (*args):
    
    plt.figure(figsize=(10, 4))
    for x in args:
        plt.imshow(x)
    plt.show()