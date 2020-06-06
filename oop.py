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

    
    def checking_file_validity(self):
        return True if self.head['bits_per_sample'] == 8 and self.head['num_channels'] == 1 else False

class Coordinator:
    def __init__(self, times, head):
        self.times = times  # How much to slow
        self.head = head   # File header

    def finding_old_coords(self):
        x = 0
        old_coords = []   # Ends of old unit segments
        while x < self.head['sub_chunk_2_size']:
            old_coords.append(x) # Collecting all possible old x's
            x += 1

        return old_coords

    def finding_new_coords(self):
        x = 0
        new_coords = []    # Ends of new unit segments
        while x < self.head['sub_chunk_2_size'] - 1:
            new_coords.append(x)  # Incresing amount of samples
            x += (1 / self.times)

        return new_coords

    def finding_chunk_sizes(self, new_coords):
        new_sub_chunk_2_size = len(new_coords) # Finding new characteristics of resulting file
        new_chunk_size = self.head['chunk_size'] - self.head['sub_chunk_2_size'] + new_sub_chunk_2_size
        self.head['sub_chunk_2_size'] = new_sub_chunk_2_size  # Such as subchunk2 size
        self.head['chunk_size'] = new_chunk_size              # and chunkSize 


class Interpolator:
    def __init__(self, old_coords, new_coords, new_sub_chunk_2_size, raw_data):
        self.old_coords = old_coords
        self.new_coords = new_coords
        self.new_sub_chunk_2_size = new_sub_chunk_2_size
        self.raw_data = raw_data

    def create_graph(self):  # Find by interpolation
        return interpolate.interp1d(np.array(self.old_coords), np.array(list(self.raw_data)))

    def create_samples(self, graph):
        new_samples = graph(np.array(self.new_coords)).tolist()  # Calculating from function
        for i in range(self.new_sub_chunk_2_size):
            new_samples[i] = round(new_samples[i])  # Making samples whole numbers
        return new_samples

    
class Starter:
    def __init__(self, filename):
        self.filename = filename

    def printer(self):
        with open(self.filename, 'rb') as f:
            starter = f.read()[:44]
            print(starter)