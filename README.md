
s3a Decorrelator
=============
The s3a decorrelator is an open-source upmix algorithm written in python.

The algorithm can also be used to upmix any audio source to any number of channels. The algorithm is blind and the resultant upmix remains mono compatible.

It was designed to maximise envelopment for diffuse sound objects such as ambience, applause and reverberation but can be used for any source material.

The python toolbox in this repository includes the tools needed for offline processing of audio files and includes a range of decorrelation filters.

## Introduction
The design and validation of the algorithm is fully described in an academic paper that is currently in progress.  Contact michaelcousins56@gmail.co.uk for more information.

The algorithm is formed of two stages. The first stage separates the audio into three components; transients, noise and harmonic content. The second then applies different decorrelation on these components to maximise envelopment whilst minimising the addition of artefacts.

## Audio Examples
Examples will be available [here](http://www.s3a-spatialaudio.org/research/stream-2/decorrelarion "s3a Decorrelation Webpage").

## Prerequisites
The decorrelator and toolbox is written in python and requires a python 3 distribution.
We recommend the Anaconda distribution and this is compatible with other s3a software including VISR. (Although a conda package for the s3a-decorrelation toolbox is not yet available)

The package requires: librosa, pysoundfile, scipy, acoustics, matplotlib and pyloudnorm packages. If you use `pip install` to install the package, these dependencies will be installed automatically. 

Tested with python 3.6 and 3.7.

## Installation
To install, open a terminal window (command line on windows) and use the command
```
pip install s3a-decorrelation-toolbox
```

## Example
The simplest example is 
```
import s3a_decorrelation_toolbox.s3a_decorrelator as s3a

s3a.s3a_decorrelator('/folder/input_file.wav',
'/folder/output_filename.wav', make_mono = True, duration = 10)
```
or 
```
import s3a_decorrelation_toolbox.s3a_decorrelator as s3a

s3a.s3a_decorrelator('/folder/input_file.wav',
'/folder/output_filename.wav', preset = 'upmix', make_mono = True, duration = 10)
```

This will take a wav called `input_file.wav`, convert it to mono if required (because of the `make_mono = True` argument) and then upmix the first 10 seconds (`duration = 10`) of the mono signal to stereo (the default) and finally saving the output file as `output_filename.wav`. 

The optional `preset = 'upmix'` should probably be used for generic audio upmix purposes where the voice should not be diffuse whereas the default (`preset = 'diffuse'`) is more suited to material such as rain and applause which should be diffuse.

The file `examples/demo_s3a_decorrelator.py` includes some more demonstrations of general upmix.

## Decorrelation Algoritm

The design and validation of the algorithm is fully described in an academic paper that is currently in progress but here is a breif overview.

### Background

For signals to be uncorrelated with each other, the phase relation between the signals need to vary over time. A static phase relationship between signals means that the signals are coherent. Decorrelation methods seek to maximise the randomness of the phse between the two signals. This can be acheived using two mechanisms, phase based and amplitude based. Amplitude based decorrelation is where the input signal is divided between the output signals based on frequency i.e. even frequencies in the one output signal and odd frequencies in the second output signal. Because 100 Hz is incoherent with 101 Hz. this leads to low coherence between the output signals. Phase based methods assume that input signal has a short auto correlation and can therefore is uncorrelated with itself after a delay. By adding different delays to the same signal, the output signals are uncorrelated. One of the issues with both these mechanisms is how they treat transients. Neither mechanism works well for a tranient and the typical artefact is temporal smearing where crisp impulses are replaced by the impulse response of the filters which is not a delta function. Additionally, considering materials such as rain or applause, transients represent specific events such as rain drops or individual claps that come from a single direction and dont need to be decorrelated. It is the fact that these single events come from multiple directions ar random time that leasd them to add to be noise like. But the claps/raindrops individually do not need decorrelation.

The s3a decorrelator therefore uses a preprocessing stage using a percussive-harmonic-separator to divide the signal into components that are transients, noise and harmonics. These components can then be decorrelated with an appororiate decorrelation method. 

### Default Settings

The default settings used attempt to maximise the amount of decorrelation between loudspeakers by randomly panning transinets to different loudspeakers and using optimal filters for the steady-state components (that can be longer as there is less risk of transinet smearing). This leads to better decorrelation especially for material wher transients should ome from all directions.



### Presets

`preset = '<preset_name>'` can be used to load some alternative default settings for specific use cases.

`preset = 'diffuse'` uses all default settings and maximises envelopment.
`preset = 'upmix'` uses the default steady-state decorrelation methods and filter lengths but does not decorrelate the transinets. This is ideal for upmixing any mono to stereo where the mono includes voice. The transients in voice should be grouped together spatially to avoid it sounding very unnatural. Upmix ensures all transients go to all loudspekaers with no decorrelation.
`preset == 'upmix_mono_LRCSLsRs'` upmixes mono to 5.1 in with loudspeakers ordered L, R, C, Sub, Ls, Rs. All transinets are only routed to the centre channel.
`preset == 'upmix_stereo_LRCSLsRs'` upmixes stereo to 5.1. The tranisnets remain in the left and right channels. Uncorrelated steady-state components derived from the left input channel remain on the left and visaversa for the right derived channels.

### Other Settings

`make_mono = True'` can be used to force the input audio to mono before upmixing. This is good for testing where you want to input stereo and compare upmixed stereo to the original stereo.

`duration` is the length of the output file in seconds. The decorrelation algorithm is currently not efficient and so for testing purposes, using a short durtion of 10 seconds is sesible.

`num_out_chas` is the number of output channels the output file will have.

`transient_decorrelation_method` is the name of a decorrelation object from decorr_toolbox. e.g. `dt.Lauridsen` to be used to decorrelate the transients.
`transient_decorrelation_arguments = dict()`  is a dictionary containing arguments to the tranisnet decorrelator. For example `filterLength = 20.5` would  mean the transinent decorrelator would use a length of 20.5 ms
The harmonic and noise components have similar arguments named `harmonic_decorrelation_method`, `harmonic_decorrelation_arguments`, `noise_decorrelation_method` and `noise_decorrelation_arguments` .

`transient_routing` and `steady_state_routing` are lists with the output channels for that component. For example         `steady_state_routing' = [0, 1, 2, 4, 5]` would route all noise and harmonic decorrelated outputs to channels 0, 1, 2, 4, and 5 i.e. not to the subwoofer in a 5.1 system. In this case the number of output channels (`num_out_chans = 6`) is greater than the number of decorrelated signals which is overridden by the smaller number of items in the `steady_state_routing` argument.

## Advanced examples

Some upmix examples are included in the demo_s3a_decorrelator script.

Here is another example. We wish to take the ambience from the surround channels of a 5.1 input signal, upmix them to a 22 channel loudspeaker system and add back in the original front channels and the transients to their original channels.

```
import soundfile as sf
import scipy
import s3a_decorrelation_toolbox.s3a_decorrelator as s3a

audioFile, fs = sf.read('5.1_input_filename.wav')

surround_Channels = audioFile[:,[4,5]]

audioOut = s3a.s3a_decorrelator(surround_Channels,          # input a numpy array instead of filename string.
output_filename = None,     # don't write an output file
duration = 10,              # only process the first 10 seconds
num_out_chans = 22,         # output has 22 channels
transient_routing = [4, 5], # Transients go back to the channels they came from
make_mono = False)          # Upmix from the 2 channels without summing them to mono first

audioOut[:, [0, 1 ,2 ,3 ]] += audioFile [:len(audioOut), [0, 1 ,2 ,3 ]] #add back in the non-surround channels

scipy.io.wavfile.write('output_filename.wav', fs, audioOut)
```


# Future Work
In the future this code will be ported to a realtime implementation of the separation and filtering stages.
The decorrealtor objects in decorr_toolbox will be updated to instead generate filters an outing matricies for the [VISR convolver](https://cvssp.org/data/s3a/public/VISR/visr_installers/0.12.0/macosx/build_py36/doc/userdoc/html/using-standalone-renderers.html#the-matrix-convolver-renderer "VISR matrix convolver renderer").


