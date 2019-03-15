#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 11:39:52 2019
Script to Demonstrate the s3a decorrelator

Takes a stereo file specified using imput_file and decorrelates using different methods.

Some methods will first down mix to mono to demonstrate mono upmix.
Others will take the stereo and upmix to multichannel.



@author: Michael Cousins
"""

from . import s3a_decorrelator as s3a


fs = 48000
duration = 10

input_file = '/Users/mike/Documents/Audio/YoutubeRip/Help.wav'
output_folder = 'Audio/Upmix/'

#================
#Upmix from mono to Stereo for diffuse material such as reverberation, rain or applause

output_filename = 's3a_Decorrelated_Audio_Diffuse.wav'
output_filename = '{fol}{fil}'.format(fol = output_folder, fil = output_filename)


s3a.s3a_decorrelator(input_file,
                     output_filename,
                     preset = 'diffuse',
                     duration = duration,
                     make_mono = True)

#===============
#Upmix from mono to Stereo for any material.

output_filename = 's3a_Decorrelated_Audio_Upmix.wav'
output_filename = '{fol}{fil}'.format(fol = output_folder, fil = output_filename)

s3a.s3a_decorrelator(input_file,
                     output_filename,
                     preset = 'upmix',
                     duration = duration,
                     make_mono = True)

#============
# Upmix from Stereo to 5.1(LRCSubLsRs) for any material.

output_filename = 's3a_Decorrelated_Audio_Upmix_Stereo-5.1.wav'
output_filename = '{fol}{fil}'.format(fol = output_folder, fil = output_filename)

s3a.s3a_decorrelator(input_file,
                     output_filename,
                     preset = 'upmix_stereo_LRCSLsRs',
                     duration = duration,
                     make_mono = False)

