import binascii
from scipy import interpolate
import numpy as np
from copy import deepcopy
from sys import exit


print('This program slows down 8-bit mono .wav files')
print('You can also speed them up by typing [xxx.yyy]<1')
print('\n')
input = input('[inputfilename.wav] [outputfilename.wav] [xxx.yyy](times slower): ').split()
filename = input[0]
with open(filename, 'rb') as f:
    content = f.read()
hexdata = binascii.hexlify(content)
hexdata = hexdata.decode("utf-8")
split_bytes = []
for i in range(0, len(hexdata), 2):
    split_bytes.append(hexdata[i:i+2])

NumChannels = split_bytes[22:24][::-1]
NumChannels = int(''.join(NumChannels), 16)
BPS = int(''.join(split_bytes[34:36][::-1]), 16)
if NumChannels != 1 or BPS != 8:
    exit("This program is only for 8-bit mono files!")

SubChunk1Size = int(''.join(split_bytes[16:20][::-1]), 16)
HeaderSize = 44 + SubChunk1Size - 16
Subchunk2Size = int(''.join(split_bytes[HeaderSize-4:HeaderSize][::-1]), 16)

Header = split_bytes[:HeaderSize]
Data = split_bytes[HeaderSize:]
for i in range(Subchunk2Size+1):
    Data[i] = (int(Data[i], 16) / 256)
q = float(input[2])
new_size = int(Subchunk2Size*q)

old_coords = []
for x in range(Subchunk2Size+1):
    old_coords.append(x)

x=0
new_coords = []
while x <= Subchunk2Size-1:
    new_coords.append(x)
    x += (1/q)
graph = interpolate.interp1d(np.array(old_coords), np.array(Data))
new_data = graph(np.array(new_coords))
new_data = list(new_data)
for i in range(len(new_data)):
    new_data[i] = int(new_data[i]*256)
    new_data[i] = hex(new_data[i])
    new_data[i] = new_data[i].replace('0x', '')
    if len(new_data[i]) == 1:
        new_data[i] = '0' + new_data[i]


Subchunk2Code = hex(new_size).replace('0x', '')
if len(Subchunk2Code) % 2 == 1:
    Subchunk2Code = '0' + Subchunk2Code
new_len_array = []
for i in range(0, len(Subchunk2Code), 2):
    new_len_array.append(Subchunk2Code[i:i+2])
new_len_array = new_len_array[::-1]
while len(new_len_array) < 4:
    new_len_array.append('00')

new_header = deepcopy(Header)
new_header[HeaderSize-4:HeaderSize] = new_len_array

res = new_header + new_data + ['00']

res = ''.join(res)
res = res.encode('utf-8')
res = binascii.unhexlify(res)
with open(input[1], 'wb') as output:
    output.write(res)