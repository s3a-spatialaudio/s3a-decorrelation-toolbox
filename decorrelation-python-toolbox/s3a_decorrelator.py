#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 12:24:03 2019
Demonstration of the Percussive-Harmonic based decorrelator
@author: mike
"""

import percussive_harmonic_decorrelator as phdc
import scipy.io.wavfile
import soundfile as sf
import numpy as np
import decorr_toolbox as dt
import utils.test_tone_generator as ttg



def s3a_decorrelator(input_file, output_filename, duration = None, make_mono = False, fs = 48000, **kwargs):
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
    audioOut = phdc.s3a_audio_decorrelator(audioIn, **kwargs)
    scipy.io.wavfile.write(output_filename, fs, audioOut)
    return audioOut


def s3a_decorrelator_presets (input_file, output_filename, preset = 'diffuse', duration = None, make_mono = False, **kwargs):
    
    
    kw_args = dict()
    
    if preset == 'upmix':
        kw_args['transient_decorrelation_method'] = dt.Copier
        
    elif preset == 'diffuse':
        kw_args['transient_decorrelation_method'] = dt.TransientPanner

    elif preset == 'upmix_mono_LRCSLsRs':
        kw_args['transient_decorrelation_method'] = dt.Copier
        kw_args['num_out_chans'] = 6
        kw_args['transient_routing'] = [2]
        kw_args['steady_state_routing'] = [0, 1, 2, 4, 5]
        make_mono = True
        
    elif preset == 'upmix_stereo_LRCSLsRs':
        kw_args['transient_decorrelation_method'] = dt.TransientPanner
        kw_args['num_out_chans'] = 6
        kw_args['transient_routing'] = [0, 1]
        kw_args['steady_state_routing'] = [0, 1, 2, 4, 5]    
        make_mono = False
 
    elif preset == 'upmix_lauridsen4':
        kw_args['transient_decorrelation_method'] = dt.Copier
        kw_args['harmonic_decorrelation_method'] = dt.Lauridsen
        kw_args['harmonic_decorrelation_arguments'] = dict(filterLength = 10)
        kw_args['noise_decorrelation_method'] = dt.Lauridsen
        kw_args['noise_decorrelation_arguments'] = dict(filterLength = 10)
    
    audioOut = s3a_decorrelator(input_file, 
                             output_filename,
                             duration = duration, 
                             make_mono = make_mono,
                             **kw_args)
    
    return audioOut

    