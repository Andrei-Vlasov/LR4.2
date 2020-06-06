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

    chunkSize = struct.unpack('<L', f.read(4))[0]
    print(chunkSize)
    format = f.read(4)
    if format != b'WAVE':
        print('not a WAV file')
        exit(1)

    while f.tell() < 8 + chunkSize:
        tag = f.read(4)
        subchunkSize = struct.unpack('<L', f.read(4))[0]
        print(subchunkSize)
        if tag == b'fmt ':
            Head['Subchunk1Size'] = subchunkSize
            fmtData = f.read(subchunkSize)
            fmt, numChannels, sampleRate, byteRate, blockAlign, bitsPerSample = struct.unpack('<HHLLHH', fmtData)
            Head['AudioFormat'] = fmt
            Head['NumChannels'] = numChannels
            Head['SampleRate'] = sampleRate
            Head['ByteRate'] = byteRate
            Head['BlockAlign'] = blockAlign
            Head['BitsPerSample'] = bitsPerSample

        elif tag == b'data':
            Head['Subchunk2Size'] = subchunkSize
            rawData = f.read(subchunkSize)
            break

        else:
            f.seek(subchunkSize, 1)

assert(Head['BitsPerSample'] == 8)
assert(Head['NumChannels'] == 1)

samples = np.array(list(rawData))
print(samples)

x = 0
new_coords = []  # концы новых единичных отрезков
while x < Head['Subchunk2Size']:
    new_coords.append(x)
    x += (1 / q)

# graph = interpolate.interp1d(np.array(old_coords),
#                              np.array(Data))  # 3 параметр функции - квадратная, кубическая.. см. scipy interpolate
# new_data = graph(np.array(new_coords))  # через полученную функцию пропускаем новые переменные
# new_data = list(new_data)  # np array -> array. Это обязательно?
# for i in range(len(new_data)):  # числа от 0 до 1 -> 16ичные значения
#     new_data[i] = int(new_data[i] * 256)
#     new_data[i] = hex(new_data[i])
#     new_data[i] = new_data[i].replace('0x', '')  # убираем стандартный 0х из строки
#     if len(new_data[i]) == 1:  # нам их предстоит склеивать
#         new_data[i] = '0' + new_data[i]