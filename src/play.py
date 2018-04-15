#!/usr/bin/env python3
# vim:ts=4:sts=4:sw=4:expandtab


import numpy as np
import pulseaudio as pa
import sys
import random
import os
import frames

gotFile = False
"""If we gave file to which we will be sending our sound we put name of this file as environmental variable '__PULSEAUDIO_WAVFILE__'"""
try:
    os.environ['__PULSEAUDIO_WAVFILE__'] = sys.argv[1]
    gotFile = True
except IndexError:
    pass




"""MAIN VARIABLES ALL TO BE CHANGED"""
framerate = 44100
amplitude = 2**15

freq0 = 1300
freq1 = 2600
bitsPerSec = 10


def playTheBox(line):
    #print (line)
    bit0 = (np.sin(2 * np.pi * np.arange(framerate // bitsPerSec) * freq0 / framerate) * amplitude)
    bit1 = (np.sin(2 * np.pi * np.arange(framerate // bitsPerSec) * freq1 / framerate) * amplitude)
    silence = (np.arange(framerate//bitsPerSec)*0)
    with pa.simple.open(direction=pa.STREAM_PLAYBACK, format=pa.SAMPLE_S16LE, rate=framerate, channels=1) as player:
        if gotFile is True:
            """ generating randomly lengthed silence at the beginning of our sound"""
            rand_int = random.randint(0,30)
            for i in range(rand_int):
                player.write(silence)

            """ generating randomly offset/shift of our sound """
            rand_int = random.randint(2, 9)
            player.write(np.arange((framerate//bitsPerSec)//rand_int)*0)

        """ generating our sound"""
        for bit in line:
            if bit == '0':
                player.write(bit0)
            else:
                player.write(bit1)
        player.drain()

while True:
    try:
        line = input()
        if line.startswith("quit"):
            break
        playTheBox(frames.encipher(line))
    except EOFError:
        break