#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 17 15:02:26 2018
This file includes some tools to generate audio of arbitrary number of channels using looping with offsets.

Replace the audio file names with appropriate filenames on your system.

The reverb is a nice way to get channels with as low correlation as possible for reverberation.
I use anechoic orchestral recordings from [1]

[1] J. Pätynen, V. Pulkki, and T. Lokki, “Anechoic Recording System for Symphony Orchestra,” Acta Acustica united with Acustica, vol. 94, no. 6, pp. 856–865, 2008.

@author: Michael Cousins
"""

import acoustics
import numpy as np
import soundfile as sf
import pyloudnorm as pyln
from .. import decorr_toolbox as dt

def addDim(audioIn):
    audioOut = audioIn.reshape(audioIn.shape[0],-1)
    return audioOut

def normalise (audio,targetLoudness = -20, fs = 48000):
    # measure the loudness first of the sum of all channels.
    meter = pyln.Meter(rate=fs) # create BS.1770 meter
    loudness = meter.integrated_loudness( np.sum(audio,axis=1))     
    audioOut = pyln.normalize.loudness(audio, loudness, targetLoudness)
    return audioOut

def lengthen (audioIn, l = 480000, overlap = 480):
    audioIn = audioIn.reshape(audioIn.shape[0],-1)
    audioLen = len(audioIn)
    numChans = audioIn.shape[1]
    numReps = int(np.ceil(l/(audioLen-overlap)))
    audioOut = np.zeros((audioLen*numReps,numChans))
    window = np.ones(audioLen)
    window[:overlap]=np.sqrt(np.linspace(0,1,num=overlap))
    window[-overlap:]=np.sqrt(np.linspace(1,0,num=overlap))
    for x in range(numChans):
        for n in range (numReps):
            audioOut[n*audioLen:(n+1)*audioLen,x] = audioOut[n*audioLen:(n+1)*audioLen,x] + audioIn[:,x]*window
    
    
    return audioOut
    
def loopsplit (audioIn, numChans = 2):
    audioIn = audioIn.reshape(audioIn.shape[0],-1)
    numInChans = audioIn.shape[1]
    audioLen = len(audioIn)
    
    numDivisions = int(np.ceil(numChans/numInChans))
    audioOutLen = int(np.floor(audioLen/numDivisions))
    
    
    audioOut = np.zeros((audioOutLen,numChans))

    for x in range (numChans):
        inCh = x%numInChans
        indx = x%numDivisions
        audioOut[:,x]= audioIn[indx*audioOutLen:(indx+1)*audioOutLen,inCh]
        
        
    return audioOut


def multichannelify (audioIn, numChans, l, overlap):
    audioIn = audioIn.reshape(audioIn.shape[0],-1)
    audioOut = np.zeros((l, numChans))
    
    audioOutTemp = loopsplit(audioIn, numChans = numChans)
        
    audioOutTemp2 = lengthen(audioOutTemp, l=l, overlap = overlap)
    
    audioOut = audioOutTemp2[:l,:]
    
    return audioOut

    
def audiogenerator( numChans = 2, material ='pink', t=10 ,fs =48000, targetloudness = -20):
    
    l=int(t * fs)
    audioOut = np.zeros((l,numChans))
    
    if material =='pink':
        for x in range(numChans):
            audioOut[:,x] = acoustics.generator.pink(l)
      
    elif material == 'white':
        for x in range(numChans):
            audioOut[:,x] = acoustics.generator.white(l)
        
    elif material == 'reverb':
        audioIn, sr = sf.read('/Users/mike/Documents/Code/Matlab_MC/Audio/MahlerAnechoicMono.wav')
        
        audioIn = audioIn[:l]
        Decorrelator = dt.FauxReverb(audioIn, reverbTime=2, numOutChans = numChans)
        audioOut = Decorrelator.audio_out

    elif material == 'rain':
        audioIn, sr = sf.read('/Users/mike/Documents/Audio/RainAndThunderFieldRecording/Rain_48_16_Static.wav')
        audioOut = multichannelify (audioIn, numChans=numChans, l = l, overlap =480)
        
        
    elif material == 'applause':

        audioIn, sr = sf.read('/Users/mike/Documents/Code/Matlab_MC/Audio/BBCApplause48.wav')
        audioOut = multichannelify (audioIn, numChans=numChans, l = l, overlap = 480)
    

    audioOutNorm = normalise (audioOut,targetLoudness = targetloudness, fs = fs)
    return audioOutNorm
