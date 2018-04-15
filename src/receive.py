#!/usr/bin/env python3
# vim:ts=4:sts=4:sw=4:expandtab

import numpy as np
import pulseaudio as pa
import frames
import sys
import os

"""If we gave file from which we will be getting our sound we put name of this file as environmental variable '__PULSEAUDIO_WAVFILE__'"""

try:
    os.environ['__PULSEAUDIO_WAVFILE__'] = sys.argv[1]
except IndexError:
    pass
"""MAIN VARIABLES ALL TO BE CHANGED"""
freq0 = 1300
freq1 = 2600
framerate = 44100
sync_precision = 19
bitsPerSec = 10


def checkFreq(sample):
    """ func checking if our sample frequency is near enough to be considered as our sound's frequency"""
    if abs(sample[0] - freq0) < 100:
        return 0
    elif abs(sample[0] - freq1) < 100:
        return 1
    return -1


def synchronize(recorder):
    """ func minimalizing possible shift in our sound """
    imax = -1
    best = -1
    gotNoise = False
    for i in range(sync_precision):
        """ for each move we getting sample """
        sample = getSingleSample(recorder)
        #print( "synched sample ", sample[0], sample[1] )
        if checkFreq(sample) == -1:
            gotNoise = True
            break
        """and now choosing the best sample(the most powerful)"""
        if sample[1] > best:
            best = sample[1]
            imax = i

        recorder.read((recorder.rate//bitsPerSec)//sync_precision)
    if gotNoise is False :
        recorder.read(imax*(recorder.rate//bitsPerSec)//sync_precision)
        return True
    else:
        return False



def read_preambule(recorder):
    """func getting all bits until preambule's end"""
    i = 0
    sample1 = None
    sample2 = None
    while True:
        if i == 0:
            i += 1
            sample1 = getSingleSample(recorder)
        else:
            sample2 = sample1
            sample1 = getSingleSample(recorder)
            if checkFreq(sample1) == -1 or checkFreq(sample2) == -1:
                return False
            if checkFreq(sample1) == 1 and checkFreq(sample2) == 1:
                return True



def read_message(recorder):
    """func getting all bits from the message"""
    output_msg = ''
    len_msg = 0
    i = 0
    while True:
        sample = getSingleSample(recorder)
        if checkFreq(sample) == -1:
            """if freq is not possible to be from our sound, we stop reading"""
            break
        else:
            output_msg += str(checkFreq(sample))
        i += 1
        if i == 140:
            len_msg = int(frames.convert5B4B(output_msg[120:140]), 2)
        elif i >= (18 + len_msg) * 10:
            break
    return output_msg

def getSingleSample(recorder):
    """func getting one sample(one bit) from our sound"""
    res = recorder.read(recorder.rate//bitsPerSec)
    fourier = np.abs(np.fft.fft(res))
    fourier = fourier[0:len(fourier)//2]
    freq = np.argmax(fourier)
    return freq*bitsPerSec, fourier[freq]

with pa.simple.open(direction=pa.STREAM_RECORD, format=pa.SAMPLE_S16LE, rate=framerate, channels=1) as recorder:
    while True:
        sample = getSingleSample(recorder)
        #print("sample ", sample[0], sample[1])
        if checkFreq(sample) != -1:
            if synchronize(recorder) is True:
                if read_preambule(recorder) is True:
                    msg = read_message(recorder)
                    print( frames.decipher(frames.convert5B4B(msg)) )




