import struct
from scipy import interpolate  # interpolation function
import numpy as np  # interpolation works only to numpy arrays

class FileWorker:
    def __init__(self, filename):
        self.filename = filename
        self.head = {}
        self.raw_data = None

    def get_file_properties(self):
        with open(self.filename, 'rb') as f:
            chunk_id = f.read(4)   # Here we get Id of chunk
            if chunk_id != b'RIFF':  # Checking file type validity
                print("File is not RIFF-type")
                return None
            
            self.head['chunk_id'] = 'RIFF'  # Declared file chunk type


            
            