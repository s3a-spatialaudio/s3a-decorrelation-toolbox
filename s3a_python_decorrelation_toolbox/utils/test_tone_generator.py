#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  4 12:02:45 2019
Testing the decorrelation of differnt test signals that may be used for Task 2 
experiment 4. Decorrelation methods and anounts for a Percussive Harmonic based 
decorrelator.
@author: mike
"""

import sys
sys.path.append('/Users/mike/Documents/Code/PythonDecorrelationToolbox')

import percussive_harmonic_decorrelator as phdc
import utils.audio_generators as ag
import scipy.io.wavfile
import soundfile as sf
import numpy as np
import decorr_toolbox as dt

fs = 48000

def generateNoise(duration, fs = 48000):

    audio = ag.audiogenerator( numChans = 1, material ='pink', t = duration ,fs = fs, targetloudness = -20)
    
    return audio


def ms2samp(timeInMs, fs):
    NumSamples = int(timeInMs/1000*fs)
    return NumSamples
    
    
def convertToBurstTrain(audio, onTime = 500, offTime = 500 , attack = 10, decay = 10, fs = 48000):
    onTime = ms2samp(onTime, fs)
    offTime = ms2samp(offTime, fs)
    attack = ms2samp(attack, fs)
    decay = ms2samp(decay, fs)
    lPeriod = onTime+offTime
    numReps = len(audio)//lPeriod
    l = lPeriod * numReps
    envelopePeriod = np.zeros(lPeriod)
    envelopePeriod[:onTime] = 1
    envelopePeriod[:attack] = np.linspace(0, 1, num = attack)
    envelopePeriod[onTime-decay:onTime] = np.linspace(1, 0, num = decay)

    
    envelope = np.tile(envelopePeriod,(1,numReps))
    audioOut = np.multiply(np.squeeze(audio[:l]), np.squeeze(envelope))
    
    
    return audioOut

def addSineModulation(audio, Frequency = 1, fs = 48000):
    l = len(audio)
    t = np.linspace(0, l, num=l)
    sin = (np.sin(2*np.pi*Frequency*t/fs) + 1)/2
    audioOut = np.multiply(np.squeeze(audio), sin)
    audioOut = audioOut.reshape(audioOut.shape[0],-1)

    return audioOut

def generateSineWave(frequency, duration, fs = 48000):
    l = int(duration * fs)
    t = np.linspace(0, duration, num=l)
    sin = np.sin(2*np.pi*frequency*t)
    
    return sin


def generateChord(frequencies, duration = 1, waveType = "sine", attack = 10, decay = 10, fs = 48000):
    l = duration * fs
    infade = int(attack/1000*fs)
    outfade = int(decay/1000*fs)

    audioOut = np.zeros((l,1))
    for f in frequencies:
        if waveType == "sine":
            wave = generateSineWave(f, duration)
        elif waveType == "square":
            wave = generateSquareWave(f, duration)
        elif waveType == "sawtooth":
            wave = generateSawtoothWave(f, duration)

        #add fade in and out
        wave[:infade] = wave[:infade]*np.linspace(0, 1, num = infade)
        wave[-outfade:] = wave[-outfade:]*np.linspace(1, 0, num = outfade)
        wave = wave.reshape(wave.shape[0],-1)
    
        audioOut = audioOut + wave

    return audioOut

def generateSquareWave (frequency, duration):
    square = generateSineWave(frequency, duration)
    square = np.sign(square)
    return square

def generateSawtoothWave (frequency, duration, fs = 48000):
    l = duration*fs
    a = fs/frequency #Period in samples
    t = np.linspace(0, l, num = l)
    sawtooth = 2*(t/a - np.floor(1/2 + t/a))
    return sawtooth

#testAudio = generateChord((440, 880, 1320, 1980, 660, 990 ), duration = 10, waveType = "square" )
#testAudio = generateNoise(duration= 10)
#test2 = addSineModulation(testAudio)
#test3 = convertToBurstTrain(testAudio)


#
#
#ComponentAudio = phdc.separateMultiAudio(testAudio)
#
#Decorrelator = dt.Lauridsen(ComponentAudio['Harmonic'], filterLength = 7 )
#decorrAudio = Decorrelator.decorrelateAudio()
#
#
#filename = 'Audio/OrigTrainTest.wav'
#scipy.io.wavfile.write(filename, fs, testAudio)
#
#filename = 'Audio/DecorrTrainTest.wav'
#scipy.io.wavfile.write(filename, fs, decorrAudio)
#    
#filename = 'Audio/NoiseTrainTest.wav'
#scipy.io.wavfile.write(filename, fs, ComponentAudio['Harmonic'])  
