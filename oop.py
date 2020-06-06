from struct import pack, unpack
from scipy import interpolate  # interpolation function
import numpy as np  # interpolation works only to numpy arrays

class FileWorker:
    def __init__(self, filename):
        self.filename = filename
        self.head = {}
        self.raw_data = None

    def get_file_properties(self):
        with open(self.filename, 'rb') as f:
            # Processing RIFF chunk descriptor
            chunk_id = f.read(4)   # Here we get Id of chunk
            if chunk_id != b'RIFF':  # Checking file type validity
                print("File is not RIFF-type")
                return None
            
            self.head['chunk_id'] = 'RIFF'  # Declared file chunk type

            chunk_size = unpack("<L", f.read(4))[0]  # Finding chunk size
            self.head['chunk_size'] = chunk_size  # Declared chunk size

            file_format = f.read(4)
            if file_format != b'WAVE':  # Checking file format
                print("File is not WAV format")
                return None
            self.head['file_format'] = 'WAVE'  # Declaring file format
            
            # Processing fmt and data subchunk
            while f.tell() < 8 + chunk_size: # Scrolling through left file
                tag = f.read(4)   # Checking every byte combination
                sub_chunk_size = unpack('<L', f.read(4))[0]
                # Checking what info contains a tag we found 
                if tag == b'fmt ':   # 'fmt ' subchunk
                    self.head['sub_chunk_1_id'] = 'fmt '
                    self.head['sub_chunk_1_size'] = sub_chunk_size
                    fmt_data = f.read(sub_chunk_size)
                    fmt, num_channels, sample_rate, byte_rate, block_align, bits_per_sample = unpack('<HHLLHH', fmt_data)
                    self.head['audio_format'] = fmt
                    self.head['num_channels'] = num_channels
                    self.head['sample_rate'] = sample_rate
                    self.head['byte_rate'] = byte_rate
                    self.head['block_align'] = block_align
                    self.head['bits_per_sample'] = bits_per_sample
                # 'data' subchunk
                elif tag == b'data':
                    self.head['sub_chunk_2_id'] = 'data'
                    self.head['sub_chunk_2_size'] = sub_chunk_size
                    self.raw_data = f.read(sub_chunk_size)
                    break   # We have already read all data
                # In case subchunk type not 'fmt ' or 'data'
                else:
                    f.seek(sub_chunk_size, 1) 