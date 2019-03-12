
s3a Decorrelator
=============
The s3a decorrelator is an open-source upmix algorithm written in python.

The algorithm can also be used to upmix any audio source to any number of channels. The algorithm is blind and the resultant upmix remains mono compatible.

It was designed to maximise envelopment for diffuse sound objects such as ambience, applause and reverberation but can be used for any source material.

The python toolbox in this repository includes the tools needed for offline processing of audio files and includes a range of decorrelation filters.

## Introduction
The design and validation of the algorithm is fully described in an academic paper that is currently in progress.  Contact m.cousins@surrey.ac.uk for more information.

The algorithm is formed of two stages. The first stage separates the audio into three components; transients, noise and harmonic content. The second then applies different decorrelation on these components to maximise envelopment whilst minimising the addition of artefacts.

## Examples
Examples can be found here.

## Prerequisites
The decorrelator and toolbox is written in python and requires a python 3 distribution.
We recommend the Anaconda distribution and this is compatible with other s3a software including VISR.

## Installation
To install, open a terminal window (command line on windows) and use the command
```
pip install s3a-decorrelator
```
or if using Anaconda
```
conda install s3a-decorrelator
```

## Usage
The simplest example is 
```
import s3a-decorrelator as s3a

s3a.s3a_decorrelator('Folder/mono_input_file.wav',
'folder/subfolder/output_filename.wav')
```

The file `Examples/demo_s3a_decorrelator.py ` includes some more demonstrations of general upmix.
