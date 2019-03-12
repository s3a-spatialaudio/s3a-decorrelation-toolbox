#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 11:39:52 2019
Script to Demonstrate the s3a decorrelator
@author: mike
"""



import s3a_decorrelator as s3a


fs = 48000
duration = 10

input_file = '/Users/mike/Documents/Audio/YoutubeRip/Help.wav'


output_filename = 's3a_Decorrelated_Audio.wav'
output_folder = 'Audio/Upmix/'
output_filename = '{fol}{fil}'.format(fol = output_folder, fil = output_filename)


audioOut = s3a.s3a_decorrelator_presets(input_file, 
                                        output_filename,
                                        preset = 'upmix_lauridsen4',
                                        duration = duration, 
                                        make_mono = True)






