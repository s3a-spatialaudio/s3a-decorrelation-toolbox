#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 14:12:22 2019
Decorrelation Toolbox In Class structure.

Tools for generating the filters as well as structures of decorrelation modules.
Decorrelation modules allow the input of multichannel audio to upmix to a greater number of channels as well as creating arbitrary numbers of channels when using complementary filters that are usually limited to 2 ouputs per input.

Includes:

Lauridsen: Complementary comb filters [1]
AllPass: White noise burst FIR filters [2]
Fink: Complementary Symmetrical White Noise Bursts [3]
VelvetNoise: Random Implulse FIR filter (sparse noise) [4]
TransientPanner: Panning individual transients to random loudspeakers.
FauxReverb: White noise burst with exponential decay. Similar to a perfectly diffuse reverberation tail.
Copier: No decorrelation. Jut duplication across loudspeakers.
FreqLauridsen: Complementary comb filters with notches spaced logarithmically with frequency.
AllPassLauridsen: Complementary filters like Lauridsen but using noise instead of delays.


[1] M. R. Schroeder ‘An Artifical Stereophonic Effect Obtained from a Single Audio Source’, Journal of the Audio Engineering Society, Volume 6, Number 2, 1958.
[2] G. S. Kendall, “The Decorrelation of Audio Signals and Its Impact on Spatial Imagery,” Computer Music Journal, vol. 19, no. 4, p. 71, 1995.
[3] M. Fink, S. Kraft, U. Zölzer, T. P. Daf. Crew, J. Fourier, and C. Shannon, “Downmmix-compatible Conversion from Mono to Stereo in Time- and Frequency-Domain,” p. 4, 2015.
[4] B. Alary, A. Politis, and V. Välimäki, “Velvet-Noise Decorrelator,” International Conference on Digital Audio Effects, vol. 21th International Conference on Digital Audio Effects (DAFx–18), p. 7, 2017.



Example Usage:
    decorrelator = dt.AllPassLauridsen(audioIn, filterLength = amount, numOutChans=layout)
    audioOut = decorrelator.audio_out
    
@author: Michael Cousins
"""
from abc import ABCMeta, abstractmethod

import numpy as np
import librosa


class Decorrelator(object):
    
    __metaclass__ = ABCMeta
    
    # Fitlers that are complementary (i.e. in pairs e.g. Lauridsen) can only double the number of channels. 
    # Therefore to creat more than one channel, the filters must be cascaded.
    # A default decorrelator object does not cascade filters.
    cascade = False
    
    def __init__(self, audioIn, fs = 48000, numOutChans = 2, decorr_method = None):
        self.decorr_method = decorr_method
        # Sampling frequency
        self.fs = fs
        #Number of output channels.
        self.numOutChans = numOutChans
        # Audio in as a 2D numpy array
        self.audioIn = add_dimension(audioIn)
        # Number of input channels.
        self.numInChans = self.audioIn.shape[1]
        self.audio_out = self.decorrelateAudio()


    def decorrelateAudio(self):
        # Running this function generates the decorrelated audio.
        # It runs a selection of decorrelator modules based on the number of input channels.
        # Each decorrelator module is the decorrelate() function that is 
        # dependent on the specific decorrelator.
        
        # Split the decorreltion into mini decorrelations based on number of input channels.
        
        #                            ___
        #                           |   |__1___
        #                ___1_______|D2 |
        #                           |   |__2___
        #                           |___| 
        #                            ___
        #                           |   |__3___
        #                           |D3 |
        #    3 Channel In___2_______|   |__4___       
        #                           |   | 
        #                           |   |__5___       8 Channel Out
        #                           |___| 
        #                            ___    
        #                           |   |__6___  
        #                ___3_______|D3 |
        #                           |   |__7___
        #                           |   |
        #                           |   |__8___
        #                           |___|   
        #
        # Decorrelation from 3 input channels to 8 channel outputs requires 1x 2ch decorrelator module and 2x3 channel decorrelator module
        
        
        AudioOut = []

        
        for n in range(self.numInChans):
            
            # division into decorrelation modules.
            if n < self.numOutChans%self.numInChans:
                numOuts = self.numOutChans//self.numInChans + 1
            elif n >= self.numOutChans%self.numInChans:
                numOuts = self.numOutChans//self.numInChans
                
            audio = self.audioIn[:,n]
            audio = audio.reshape(audio.shape[0],-1)

            
            if numOuts > 1:
                # decorrelate either using a cascade of filters or a single multichannel filter bank.
                if self.cascade == True:
                    #Decorrelate the input audio based on a cascade of different filter lengths
                    audioOutTemp = self.decorrelationCascade(audio, numOuts)
                    
                    
                elif self.cascade == False:
                    #Directly Decorrelate all the Audio.
                    audioOutTemp = self.decorrelationDirect(audio, numOuts)
            
            #In the case not all channels need to be decorrelated...
            elif numOuts ==1:
                audioOutTemp = audio
            else:
                print('error: maybe too many inputs channels not enough output channels')

                       
            # pad the shorter and add to the output.
            AudioOut.append(audioOutTemp)
            
        #combine all the outputs in single output file
        # pad the shorter arrays to match the longer.
        length = 0
        for n in AudioOut:
            length = max (length, len(n))
       
        for n in range(len(AudioOut)):
            #pad shorter arrays
            AudioOut[n] = np.pad(AudioOut[n], [(0, length - len(AudioOut[n])), (0, 0)], mode='constant', constant_values=0)
        AudioOutFinal = AudioOut[0]
        
        for n in range(len(AudioOut)-1):
            AudioOutFinal = np.hstack((AudioOutFinal, AudioOut[n + 1]))
            

        return AudioOutFinal



    def decorrelationDirect(self, audio, numOuts):
        # Direct decorrelation has no need for cascading filters, all filtering can be done at once.
        audioOut = self.decorrelate(audio, numOuts)

        return audioOut
        
        
    def decorrelationCascade(self, audio, numOuts):
        # If decorrelation is limited by doubling of channels then cascade multiple decorrelators with varying length. 
        # Take 1 input and output M signals by decorrelation (filter determined by the decorrelate method)
        #                            ______
        #                      _____|
        #              _______|     |______
        #             |       |      ______ 
        #  1 In ______|       |_____|          6 Out
        #             |             |______
        #             |        ____________
        #             |_______|
        #                     |____________
        #
        #
        #           ^------------^^-------^
        #          2 Full stages    2 Part stage Channel
    
    
        numFullStages = int(np.floor(np.log2(numOuts)))
        partStageChans = numOuts-2**numFullStages
        # filter length will halve on each stage.
        filterLength = self.filterLength
        
        
        for n in range(numFullStages):
            
            audioOut = self.decorrelate(audio, filterLength)
            audio = audioOut
            filterLength = filterLength/2

        if partStageChans > 0:
            audioOutTemp = self.decorrelate(audio[:,:partStageChans], filterLength)
            audioOut = np.pad(audio[:,partStageChans:], ((0, len(audioOutTemp)-len(audioOut)), (0, 0)), 'constant')
            audioOut = np.concatenate((audioOutTemp,audioOut), axis=1)

        # Normalise the output r.m.s to match the input. 
        scale = np.sqrt(np.mean(np.square(self.audioIn)))/  np.sqrt(np.mean(np.square(np.sum(audioOut, axis=1))))
        audioOut = audioOut*scale
        
        return audioOut
    
    def ms2samp (self, filterLength):
        NumSamples = int((filterLength / 1000) * self.fs)

        return NumSamples
    

    
    @abstractmethod
    def decorrelate():
        """"Decorrelate the audio using specific method."""
        pass
    
    
    
    
    
class AllPass(Decorrelator):
    
    cascade = False
    
    def __init__(self, audioIn, filterLength = 9.213 , **kwargs):
        self.filterLength = filterLength
        
        super().__init__(audioIn, **kwargs)


    def decorrelate(self, audio, numOuts):
        """"Decorrelate using AllPass"""
        Filters = self.genAllPass(self.filterLength, numOuts)

        audioOut = np.zeros((len(audio)+self.ms2samp(self.filterLength)-1, numOuts))
        for n in range(numOuts):
            audioOut[:,n] = np.convolve(np.squeeze(audio),Filters[:,n])
    
        scale = np.sqrt(np.mean(np.square(audio)))/  np.sqrt(np.mean(np.square(np.sum(audioOut, axis=1))))
        audioOut = audioOut*scale
        return audioOut  
        
    def genAllPass(self, filterLength , numChans):
        #Filterlength in ms. Default is generally ok for Stereo based on minimal artefacts.
        filterLength = self.ms2samp (filterLength)
        
        Filters = np.zeros((filterLength,numChans))
       
        for n in range(numChans):
            
            phases=np.random.uniform(low = 0,high = 2*np.pi, size = filterLength//2)
            a=np.zeros(filterLength,dtype=np.complex)
            a[1:filterLength//2 + 1] = np.exp(np.multiply(1j,phases))
            a[-(filterLength//2) :] =a[-(filterLength//2) :] + np.exp(np.flipud(np.multiply(-1j,phases)))
            a[0] = 0
            Filters[:,n]=np.fft.ifft(a).real
        
    
        return Filters




class Lauridsen(Decorrelator):
    
    cascade = True

    def __init__(self, audioIn, filterLength = 10.4, **kwargs):
        self.filterLength = filterLength
        
        super().__init__(audioIn, **kwargs)

    def decorrelate(self, audio, filterLength):
        """"Decorrelate using Lauridsen. Returns double the number of inputs"""

        Filters = self.genFilter(filterLength)
        numInChans = audio.shape[1]
        numOutChans = (numInChans)*2
        audioDouble= np.concatenate((audio,audio), axis=1)
        audioOut = np.pad(audioDouble, ((0, len(Filters)-1), (0, 0)), 'constant')
        for ch in range(numOutChans):
            audioOut[:,ch] = np.convolve(audioDouble[:,ch],Filters[:,ch//numInChans])
        return audioOut


    def genFilter(self, filterLength = 3.379):
        filterLength = self.ms2samp (filterLength)#Convert ms to whole number of samples
        Filters = np.zeros((filterLength + 1,2))
        Filters[0,:] = 0.5
        Filters[filterLength,0] = 0.5
        Filters[filterLength,1] = -0.5 
        
        return Filters  


class AllPassLauridsen(Lauridsen):
    
    cascade = True
    
    def __init__(self, audioIn, filterLength = 65, **kwargs):
        self.filterLength = filterLength
        
        super().__init__(audioIn, filterLength, **kwargs)
        
    def genFilter(self, filterLength ):

        AllPassFilter = AllPass.genAllPass(self, filterLength, numChans = 1)
        
        Filters = np.zeros((self.ms2samp(filterLength),2))
        Filters[:,0] = np.squeeze(AllPassFilter)
        Filters[:,1] = -AllPassFilter.ravel()
        Filters[0,:] = 1
        return Filters  

class Fink(Lauridsen):
    
    cascade = True
    
    def __init__(self, audioIn, filterLength, **kwargs):
        self.filterLength = filterLength
        
        super().__init__(audioIn, filterLength, **kwargs)
        
    def genFilter(self, filterLength ):
        D = self.ms2samp(filterLength/2)

        w = 1 #Stereo width parameter
        
        b = np.random.normal(0, 25, D);

        b = 0.5 + np.arctan(b* w**2) / np.pi;
        
        B = np.hstack((b, b[0], np.conj(b[::-1])));
        x = np.real(np.fft.fftshift(np.fft.ifft(B)));

        y = np.real(np.fft.fftshift(np.fft.ifft(1-B)));
        
        Filters = np.hstack((add_dimension (x),add_dimension (y)))
     
        return Filters  

    
class FreqLauridsen(Lauridsen):
    
    cascade = True
    
    def __init__(self, audioIn, filterLength = 13, **kwargs):
        self.filterLength = filterLength
        
        super().__init__(audioIn, filterLength, **kwargs)
        
    def genFilter(self, filterLength = 8.4427):
        #Filter length is the number of periods for the delay.
        #Generate a sine sweep by iteratively advancing the phase and choosing a new sample value based on the current desired frequency.
        length = int(np.ceil(self.fs/20*filterLength))
        intermediateLen = length+self.fs
        previousphase = 0   #variable to hold the current phase of the sine sweep
        SineSweep = np.zeros (intermediateLen);
        
        for n in range (1,intermediateLen-1):
            t=n/self.fs#%delay from the beginining of the sweep
            f=filterLength*self.fs/n #frequency at sample n is given by...fs x alpha 
            SineSweep[n] = np.sin(2*np.pi*f*t+previousphase)#calculate value n of the sinesweep
            previousphase = (2*np.pi*f/self.fs)+previousphase
        
        #Equlise to give a flat frequency response esp for short filter lengths.
        C=np.fft.fft(SineSweep)
        zz=np.multiply(np.ones(len(C)),np.exp(np.multiply(1j,np.angle(C))))#Restore the linear frequency response
        YY=np.fft.ifft(zz)#Restore the impulse response now with correct frequency response.
        
        # Filter length is determined by the filterlength required for 20Hz.
        
        if length > self.fs:
            print('The Filter is over 1 second long ({m} seconds)'.format( m=length/self.fs))
        CousinsFilter = np.real(YY[0:length])# truncate the filter. the real is only needed at very short filter lengths. not sure why at the moment.
    
        #Turn the sine sweep into a pair of complementary comb filters.
        Filters = np.zeros((length,2))
        Filters[:,0] = CousinsFilter
        Filters[:,1] = -CousinsFilter
        Filters[0,:] = 1
        
        return Filters  




class TransientPanner(Decorrelator):
    
    cascade = False
    
    def __init__(self, audioIn, panning_method = 'random', **kwargs):
        
        self.panning_method = panning_method
        super().__init__(audioIn, **kwargs)

    def decorrelate(self, audioIn, numOuts):
        #detect onsets 
        audioIn = np.squeeze(audioIn)
        onset_frames = librosa.onset.onset_detect(y=audioIn, sr=self.fs, backtrack=True)
        onset_samples = librosa.frames_to_samples(onset_frames)
        #select a random loudspeaker for each detected transient.
        selectChannel = self.transposition(numTrans=len(onset_frames), numChans = numOuts )
        audioOut = np.zeros((len(audioIn),numOuts))
        #Divide the input audio based on the onsets and pan to loudspeaker.
        for x in range(len(onset_frames)-1):
            audioOut[onset_samples[x]:(onset_samples[x+1]),selectChannel[x]] = audioIn[onset_samples[x]:(onset_samples[x+1])]
        return audioOut
    
    def transposition (self, numTrans, numChans = 2 ):
        
        if self.panning_method == 'random':
            selectChannel = np.random.randint(numChans, size=numTrans)
        elif self.panning_method == 'frequency':
        #TODO change this to division based on the ferquency content of the transients.
            selectChannel = np.random.randint(numChans, size=numTrans)
            
        return selectChannel
    
    
class FauxReverb(Decorrelator):
    
    cascade = False
    
    def __init__(self, audioIn, reverbTime=2, **kwargs):
        self.reverbTime = reverbTime
        super().__init__(audioIn, **kwargs)    
    

    def decorrelate(self, audioIn, numOuts ):
        lr= self.reverbTime*self.fs
        noises = np.random.randn(lr, numOuts)
        audioOut = np.zeros((len(audioIn)+lr-1,numOuts))        
        window = np.exp((-np.linspace(1,lr, num=lr))*(-np.log10(0.001)/lr));
    
        for x in range(numOuts):
            Filter = noises[:,x]*window
            audioOut[:,x] = np.convolve(audioIn, Filter)
        
        scale = np.sqrt(np.mean(np.square(audioIn)))/  np.sqrt(np.mean(np.square(np.sum(audioOut, axis=1))))
        audioOut = audioOut*scale    
        return audioOut


class Copier(Decorrelator):
    
    cascade = False
    
    def __init__(self, audioIn, **kwargs):

        super().__init__(audioIn, **kwargs)    
    

    def decorrelate(self, audioIn, numOuts ):

        audioOut = np.repeat(audioIn,numOuts, axis=1)       
    
        #Normailise gains assuming incoherent summing. (technically faulse but usuually sounds alright)
        # Equivalent of -3dB panning as opposed to 6dB panning
        gain = 1/ np.sqrt(numOuts)
        audioOut = audioOut*gain    
        return audioOut



class VelvetNoise(Decorrelator):
    
    cascade = False
    
    def __init__(self, audioIn, filterLength=442, density= 3000, **kwargs):
        self.filterLength = filterLength
        self.density = density
        super().__init__(audioIn, **kwargs)    
    

    def decorrelate(self, audioIn, numOuts ):
        
        audioOut = np.zeros((len(audioIn)+self.filterLength-1,numOuts))
        Filters = self.genvelvetnoise(filterLength=self.filterLength, density = self.density)
        
        for x in range(numOuts):
            Filter = Filters[:,x]
            audioOut[:,x] = np.convolve(audioIn, Filter)
                
        scale = np.sqrt(np.mean(np.square(audioIn)))/  np.sqrt(np.mean(np.square(np.sum(audioOut, axis=1))))
        audioOut = audioOut*scale
        
        return audioOut      
    
    def genvelvetnoise(self, filterLength=442, density = 3000):
        Filters = np.zeros((self.filterLength,self.numChans))
        Td = self.fs/density #average period.
        M = int(np.floor(filterLength/Td))#Total NUmber of Impulses
        
        for n in range(self.numChans):
            #phases=np.random.uniform(low = 0,high = 2*np.pi, size = filterLength//2-1)
            r1 = np.random.uniform(low=0,high=1, size = M)
            r2 = np.random.uniform(low=0,high=1, size = M)
            s = (2*np.round(r1)) -1  # Amplitude of the impulse
            k = np.zeros(filterLength)
            for m in range(M):
                k[m] = round((m*Td + r2[m]*(Td-1))) #Index of impulse number m
            x = np.zeros(filterLength)
            for m in range(M):
                x[int(k[m])] = s[m]
            Filters[:,n]=x
            
        return Filters
    
def add_dimension (signal):
    signal = signal.reshape(signal.shape[0],-1)
    return signal
