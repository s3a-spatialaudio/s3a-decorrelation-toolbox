#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 21:06:19 2018

This file includes the necessary tools to decorelate transients harmoic and noise components separately.

This includes functions to separate audio into transients, harmonic and noise
components and then to process these separately using decorrelators in the decorrelation toolbox.


@author: Michael Cousins
"""



from __future__ import print_function

import numpy as np

import librosa
import librosa.display
from . import decorr_toolbox as dt


def separate_mono_audio(audio, 
                      fftTrans = 1024, 
                      fftHarm = 2048, 
                      marginTrans = 2.14, 
                      marginHarm = 3.0):
    
    #Separates mono audio file into transients harmonic and noise components. based on given settings.
    
    D_stage1 = librosa.stft(audio,n_fft=fftTrans)
    D_harmonic1, D_transient = librosa.decompose.hpss(D_stage1, 
                                                      margin=(1.0, marginTrans))
    Transients = librosa.istft(D_transient)
    #TODO simplify using the transient and harmonic component extraction from librosa rather than the hpss which does both and isnt needed. Find out how to select the fft length
    
    D_residual1 = D_stage1 - D_transient #Residual 1 is everything except the Transients
    Residual1 = librosa.istft(D_residual1)
  
    D_2 = librosa.stft(Residual1,n_fft=fftHarm)
    D_harmonic2, D_percussive2 = librosa.decompose.hpss(D_2, 
                                                        margin=(marginHarm, 1.0))
    D_Noise = D_2 - D_harmonic2
    
    Harmonic = librosa.istft(D_harmonic2)
    Noise = librosa.istft(D_Noise)    
    
    return {'Transients':Transients, 'Harmonic':Harmonic ,'Noise':Noise }

def mono_audio(audio):    
    AudioOut = np.sum(audio, axis = 1)
    return AudioOut

def separate_audio (audio, 
                   fftTrans = 1024, 
                   fftHarm = 2048, 
                   marginTrans = 2.14, 
                   marginHarm = 3.0):
    
    #Separates audio file into separate components. 
    multiAudio = dt.add_dimension(audio)
    numChans = multiAudio.shape[1]
    Transients = np.zeros_like(multiAudio)
    Harmonic = np.zeros_like(multiAudio)
    Noise = np.zeros_like(multiAudio)
    for i in range(numChans):
        ComponentAudio = separate_mono_audio(multiAudio[:,i],
                                             fftTrans = fftTrans, 
                                             fftHarm = fftHarm, 
                                             marginTrans = marginTrans, 
                                             marginHarm = marginHarm)
        
        Transients[:ComponentAudio['Transients'].size,i] = ComponentAudio['Transients']
        Harmonic[:ComponentAudio['Harmonic'].size,i] = ComponentAudio['Harmonic']
        Noise[:ComponentAudio['Noise'].size,i] = ComponentAudio['Noise']
    
    return {'Transients':Transients, 'Harmonic':Harmonic ,'Noise':Noise }




def s3a_audio_decorrelator(audioIn, 
                           num_out_chans = 2, 
                           fs = 48000, 
                           transient_routing = None, 
                           steady_state_routing = None, 
                           transient_decorrelation_method = dt.TransientPanner, 
                           transient_decorrelation_arguments = dict(), 
                           harmonic_decorrelation_method = dt.Lauridsen,
                           harmonic_decorrelation_arguments = dict(),
                           noise_decorrelation_method = dt.AllPassLauridsen, 
                           noise_decorrelation_arguments = dict()):
    
       
        
        
  

    # Decorrelates the audio using using separate decorrelation methods for percussive harmonic and noise components.
    
    #Separate audio into Transinets Harmonic and Noise components.
    componentAudioIn = separate_audio(audioIn)

    # If not specified, the transients and steady-state components should be routed to random loudspeakers.
    if transient_routing is None:
        transient_routing = np.random.permutation(num_out_chans)
        
    if steady_state_routing is None:
        steady_state_routing = np.random.permutation(num_out_chans)

    # Number of output channels determined from the routing arrays.
    numTransOutChans = len(transient_routing)
    numSteadyOutChans = len(steady_state_routing)
        
    # Decorrelation+method can be used to override the default methods.

    TransientsDecorr = transient_decorrelation_method (componentAudioIn['Transients'], numOutChans = numTransOutChans,**transient_decorrelation_arguments)
    HarmonicDecorr = harmonic_decorrelation_method(componentAudioIn['Harmonic'], numOutChans = numSteadyOutChans, **harmonic_decorrelation_arguments)
    NoiseDecorr = noise_decorrelation_method(componentAudioIn['Noise'], numOutChans = numSteadyOutChans, **noise_decorrelation_arguments)

    # Different decorrelation filter lengths lead to different output lengths following the convolution.
    # Choose the minimum length and truncate the longer stimuli.
    length = min(np.array([len(HarmonicDecorr.audio_out), len(NoiseDecorr.audio_out), len(TransientsDecorr.audio_out)]))
    
    #Signals are routed to appropriate loudspeakers
    audioOut = np.zeros((length,num_out_chans))
    audioOut[:,transient_routing] = TransientsDecorr.audio_out[:length,:]
    audioOut[:,steady_state_routing] += HarmonicDecorr.audio_out[:length,:] + NoiseDecorr.audio_out[:length,:]
    
    
    return audioOut
