#!/usr/bin/env python3
# vim:ts=4:sts=4:sw=4:expandtab
import binascii


def str_to_bits(str):
    output = ''
    for i in range(len(str)):
        output += '{0:08b}'.format(ord(str[i]))
    return output


def bits_to_str(bits):
    output = ''
    for i in range(len(bits) // 8):
        output += chr(int(bits[i * 8:(i * 8 + 8)], 2))
    return output


D4B5B = {'0000': '11110', '0001': '01001', '0010': '10100', '0011': '10101', '0100': '01010', '0101': '01011',
         '0110': '01110', '0111': '01111', '1000': '10010', '1001': '10011', '1010': '10110', '1011': '10111',
         '1100': '11010', '1101': '11011', '1110': '11100', '1111': '11101'}
D5B4B = {v: k for k, v in D4B5B.items()}


def convert4B5B(message):
    return ''.join([D4B5B.get(message[i:(i + 4)]) for i in range(0, len(message), 4)])


def convert5B4B(message):
    converted_msg = ''
    for i in range(0, len(message), 5):
        if D5B4B.get(message[i:(i + 5)]) is not None:
            converted_msg += D5B4B.get(message[i:(i + 5)])
        else:
            return None
    return converted_msg


def encipher(line):
    splitted = line.split(' ', 2)
    sender = int(splitted[0])
    receiver = int(splitted[1])
    message = splitted[2]
    frame = '{0:048b}'.format(receiver) + '{0:048b}'.format(sender) + '{0:016b}'.format(len(message)) + str_to_bits(
        message)
    crc32 = binascii.crc32(int(frame, 2).to_bytes(len(frame) // 8, byteorder='big'))
    frame += '{0:032b}'.format(crc32)
    preamble = '10101010' * 7 + '10101011'
    return preamble + convert4B5B(frame)

def decipher(bits):
    if bits is None:
        pass
    elif (len(bits) >= 18 * 8):
        receiver = int(bits[0:48], 2)
        sender = int(bits[48:96], 2)
        length = int(bits[96:112], 2)
        if len(bits) == (18 + length) * 8:
            message = bits_to_str(bits[112:(112 + length * 8)])
            crc = int(bits[(112 + length * 8):], 2)
            if crc == binascii.crc32(int(bits[0:(112 + length * 8)], 2).to_bytes(14 + length, byteorder='big')):
                return sender, receiver, message
    return None, None, None

def eat_preambule(bits):
    return bits[64:]



