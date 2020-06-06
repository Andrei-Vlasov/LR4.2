import struct
Head = {}
rawData = None
from scipy import interpolate  # функция интерполяции
import numpy as np  # функция интерполяции работает с numpy массивами


# print('This program slows down 8-bit mono .wav files')
# print('You can also speed them up by typing [xxx.yyy]<1')
# print('\n')
# user = input('[inputfilename.wav] [outputfilename.wav] [xxx.yyy](times slower): ').split()  # по методичке
# filename = user[0]
# outname = user[1]
# q = float(user[2])

filename = 'laugh.wav'  # user[0]
outname = 'laugh2.wav'  # user[1]
q = 3.5   # float(user[2])


with open(filename, "rb") as f:
    chunkId = f.read(4)
    if chunkId != b'RIFF':
        print('not a valid RIFF file')
        exit(1)
    Head['ChunkID'] = 'RIFF'

    chunkSize = struct.unpack('<L', f.read(4))[0]
    Head['ChunkSize'] = chunkSize
    format = f.read(4)
    if format != b'WAVE':
        print('not a WAV file')
        exit(1)
    Head['Format'] = chunkSize

    while f.tell() < 8 + chunkSize:
        tag = f.read(4)
        subchunkSize = struct.unpack('<L', f.read(4))[0]
        if tag == b'fmt ':
            Head['Subchunk1Size'] = subchunkSize
            fmtData = f.read(subchunkSize)
            fmt, numChannels, sampleRate, byteRate, blockAlign, bitsPerSample = struct.unpack('<HHLLHH', fmtData)
            Head['Subchunk1ID'] = fmt
            Head['NumChannels'] = numChannels
            Head['SampleRate'] = sampleRate
            Head['ByteRate'] = byteRate
            Head['BlockAlign'] = blockAlign
            Head['BitsPerSample'] = bitsPerSample

        elif tag == b'data':
            Head['Subchunk2ID'] = 'data'
            Head['Subchunk2Size'] = subchunkSize
            rawData = f.read(subchunkSize)
            break

        else:
            f.seek(subchunkSize, 1)

assert(Head['BitsPerSample'] == 8)
assert(Head['NumChannels'] == 1)


x = 0
old_coords = []  # концы старых единичных отрезков
while x < Head['Subchunk2Size']:
    old_coords.append(x)
    x += 1

x = 0
new_coords = []  # концы новых единичных отрезков
while x < Head['Subchunk2Size']-1:
    new_coords.append(x)
    x += (1 / q)

new_subchunk2Size = len(new_coords)
new_chunkSize = Head['ChunkSize'] - Head['Subchunk2Size'] + new_subchunk2Size

graph = interpolate.interp1d(np.array(old_coords), np.array(list(rawData)))  # 3 параметр функции - квадратная, кубическая.. см. scipy interpolate
new_samples = graph(np.array(new_coords)).tolist()  # через полученную функцию пропускаем новые переменные


# new_rawData = struct.pack()