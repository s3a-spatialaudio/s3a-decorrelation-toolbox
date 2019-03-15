#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 12:24:03 2019
The functions in this file allow simple use of the s3a_decorrelator.
They simplify the input arguments and facilitate the use of presets to do common tasks with a single keyword.
Additional arguments can always be added to do anything custom.

@author: Michael Cousins
"""

from . import percussive_harmonic_decorrelator as phdc
import scipy.io.wavfile
import soundfile as sf
import numpy as np
from . import decorr_toolbox as dt



def s3a_decorrelator(input_file, output_filename, preset = 'diffuse', duration = None, make_mono = False, fs = 48000, **kwargs):
    
    decorrelation_arguments = preset_parser (preset, **kwargs)
    
    if type(input_file)==str:
        audioFile, fs = sf.read(input_file)
    elif type(input_file)==np.ndarray:
        audioFile = input_file
    
    if duration == None:
        l = audioFile.shape[0]
    else:
        l = np.min([fs*duration, audioFile.shape[0]])

    audioMulti = audioFile[:l]
    if make_mono == True:
        audioIn = phdc.mono_audio(audioMulti)
    else:
        audioIn = audioMulti

    # Split either the mono audio into components or the stereo audio into components to compare mono and stereo upmixes.
    audioOut = phdc.s3a_audio_decorrelator(audioIn, **decorrelation_arguments)
    
    if output_filename != None:
        scipy.io.wavfile.write(output_filename, fs, audioOut)

    return audioOut


def preset_parser (preset, **additional_kwargs):
    
    
    preset_kwargs = dict()
    
    
    if preset == 'upmix':
        preset_kwargs['transient_decorrelation_method'] = dt.Copier

        
    elif preset == 'diffuse':
        preset_kwargs['transient_decorrelation_method'] = dt.TransientPanner


    elif preset == 'upmix_mono_LRCSLsRs':
        preset_kwargs['transient_decorrelation_method'] = dt.Copier
        preset_kwargs['num_out_chans'] = 6
        preset_kwargs['transient_routing'] = [2]
        preset_kwargs['steady_state_routing'] = [0, 1, 2, 4, 5]
        
    elif preset == 'upmix_stereo_LRCSLsRs':
        preset_kwargs['transient_decorrelation_method'] = dt.TransientPanner
        preset_kwargs['num_out_chans'] = 6
        preset_kwargs['transient_routing'] = [0, 1]
        preset_kwargs['steady_state_routing'] = [0, 1, 2, 4, 5]    
 
    elif preset == 'upmix_lauridsen4':
        preset_kwargs['transient_decorrelation_method'] = dt.Copier
        preset_kwargs['harmonic_decorrelation_method'] = dt.Lauridsen
        preset_kwargs['harmonic_decorrelation_arguments'] = dict(filterLength = 10)
        preset_kwargs['noise_decorrelation_method'] = dt.Lauridsen
        preset_kwargs['noise_decorrelation_arguments'] = dict(filterLength = 10)
    
    
    allkwargs = {**preset_kwargs, **additional_kwargs}
    
    return allkwargs

    
