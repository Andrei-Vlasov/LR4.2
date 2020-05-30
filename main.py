import binascii  # Библиотека для работы с бинарными файлами
from scipy import interpolate  # функция интерполяции
import numpy as np  # функция интерполяции работает с numpy массивами
from copy import deepcopy
from sys import exit  # преждевременное завершение программы, если файл не по формату


print('This program slows down 8-bit mono .wav files')
print('You can also speed them up by typing [xxx.yyy]<1')
print('\n')
user = input('[inputfilename.wav] [outputfilename.wav] [xxx.yyy](times slower): ').split()  # по методичке
filename = user[0]
with open(filename, 'rb') as f:  # read as binary
    content = f.read()  # файл как байт-строка
hexdata = binascii.hexlify(content)  # байты из байт-строки склеиваются в байт-строку в виде последовательности 16ичных чисел
hexdata = hexdata.decode("utf-8")  # байт-строка->строка
split_bytes = []  # массив всех байтов - храним как массив строчек, потому что 16ичные числа содержат буквы
for i in range(0, len(hexdata), 2):  # добавляем в массив 16ичные значения по 2 символа из строки
    split_bytes.append(hexdata[i:i+2])

NumChannels = split_bytes[22:24][::-1]  # байты кол-ва каналов по документации
NumChannels = int(''.join(NumChannels), 16)  # перевод в 10ичное число
BPS = int(''.join(split_bytes[34:36][::-1]), 16)  # аналогично битрейт
if NumChannels != 1 or BPS != 8:  # моно? 8бит?
    exit("This program is only for 8-bit mono files!")

SubChunk1Size = int(''.join(split_bytes[16:20][::-1]), 16)  # размер 1 сабчанка меняется в зависимости от допданных
HeaderSize = 44 + SubChunk1Size - 16   # дает понять, сколько байтов содержится до самих семплов (больше 44 бывает при сжатии)
Subchunk2Size = int(''.join(split_bytes[HeaderSize-4:HeaderSize][::-1]), 16)    # кол-во битов. Последний - всегда 00? это точка?

Header = split_bytes[:HeaderSize]   # не подвергается интерполяции
Data = split_bytes[HeaderSize:]    # семплы
for i in range(Subchunk2Size+1):  # можно поиграться с рейнж. Че за гребанная 00 в конце?
    Data[i] = (int(Data[i], 16) / 256)  # (0 - 256) -> (0.0 - 1)
q = float(user[2])  # единичный отрезок интерполяции
new_size = int(Subchunk2Size*q)  # сколько будет семплов

old_coords = []  # (0, 1, 2, ..., Subchunk2Size)
for x in range(Subchunk2Size+1):  # рейнж - 00?
    old_coords.append(x)

x=0
new_coords = []  # концы новых единичных отрезков
while x <= Subchunk2Size-1:
    new_coords.append(x)
    x += (1/q)

graph = interpolate.interp1d(np.array(old_coords), np.array(Data))  # 3 параметр функции - квадратная, кубическая.. см. scipy interpolate
new_data = graph(np.array(new_coords))  # через полученную функцию пропускаем новые переменные
new_data = list(new_data)  # np array -> array. Это обязательно?
for i in range(len(new_data)):  # числа от 0 до 1 -> 16ичные значения
    new_data[i] = int(new_data[i]*256)
    new_data[i] = hex(new_data[i])
    new_data[i] = new_data[i].replace('0x', '')  # убираем стандартный 0х из строки
    if len(new_data[i]) == 1:  # нам их предстоит склеивать
        new_data[i] = '0' + new_data[i]


Subchunk2Code = hex(new_size).replace('0x', '')  # 10ный размер -> 16ый размер
if len(Subchunk2Code) % 2 == 1:
    Subchunk2Code = '0' + Subchunk2Code  #unhexify стр76 работает только с четными длиннами, добавляем старший порядок если их нечетное кол-во
new_len_array = []  # начинаем считать новый Subchunk2Size
for i in range(0, len(Subchunk2Code), 2):
    new_len_array.append(Subchunk2Code[i:i+2])  # разбиваем на байты
new_len_array = new_len_array[::-1]  # потому что little endian
while len(new_len_array) < 4:
    new_len_array.append('00')  # всегда представлен 4 байтами

new_header = deepcopy(Header)
new_header[HeaderSize-4:HeaderSize] = new_len_array  # вставляем новый размер data

res = new_header + new_data + ['00']  # все байты на выходе

res = ''.join(res)  # список - > строка
res = res.encode('utf-8')  # строка -> байт-строка с цельным значением
res = binascii.unhexlify(res)  # побайтовое разбитие строки
with open(user[1], 'wb') as output:
    output.write(res)