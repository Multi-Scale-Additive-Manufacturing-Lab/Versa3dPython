from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from struct import pack
import vtk
import math
import numpy as np


_DIFFUSION_MAPS = {
    'floyd-steinberg': (
        (1, 0,  7 / 16),
        (-1, 1, 3 / 16),
        (0, 1,  5 / 16),
        (1, 1,  1 / 16)
    ),
    'atkinson': (
        (1, 0,  1 / 8),
        (2, 0,  1 / 8),
        (-1, 1, 1 / 8),
        (0, 1,  1 / 8),
        (1, 1,  1 / 8),
        (0, 2,  1 / 8),
    ),
    'jarvis-judice-ninke': (
        (1, 0,  7 / 48),
        (2, 0,  5 / 48),
        (-2, 1, 3 / 48),
        (-1, 1, 5 / 48),
        (0, 1,  7 / 48),
        (1, 1,  5 / 48),
        (2, 1,  3 / 48),
        (-2, 2, 1 / 48),
        (-1, 2, 3 / 48),
        (0, 2,  5 / 48),
        (1, 2,  3 / 48),
        (2, 2,  1 / 48),
    ),
    'stucki': (
        (1, 0,  8 / 42),
        (2, 0,  4 / 42),
        (-2, 1, 2 / 42),
        (-1, 1, 4 / 42),
        (0, 1,  8 / 42),
        (1, 1,  4 / 42),
        (2, 1,  2 / 42),
        (-2, 2, 1 / 42),
        (-1, 2, 2 / 42),
        (0, 2,  4 / 42),
        (1, 2,  2 / 42),
        (2, 2,  1 / 42),
    ),
    'burkes': (
        (1, 0,  8 / 32),
        (2, 0,  4 / 32),
        (-2, 1, 2 / 32),
        (-1, 1, 4 / 32),
        (0, 1,  8 / 32),
        (1, 1,  4 / 32),
        (2, 1,  2 / 32),
    ),
    'sierra3': (
        (1, 0,  5 / 32),
        (2, 0,  3 / 32),
        (-2, 1, 2 / 32),
        (-1, 1, 4 / 32),
        (0, 1,  5 / 32),
        (1, 1,  4 / 32),
        (2, 1,  2 / 32),
        (-1, 2, 2 / 32),
        (0, 2,  3 / 32),
        (1, 2,  2 / 32),
    ),
    'sierra2': (
        (1, 0,  4 / 16),
        (2, 0,  3 / 16),
        (-2, 1, 1 / 16),
        (-1, 1, 2 / 16),
        (0, 1,  3 / 16),
        (1, 1,  2 / 16),
        (2, 1,  1 / 16),
    ),
    'sierra-2-4a': (
        (1, 0,  2 / 4),
        (-1, 1, 1 / 4),
        (0, 1,  1 / 4),
    ),
    'stevenson-arce': (
        (2, 0,   32 / 200),
        (-3, 1,  12 / 200),
        (-1, 1,  26 / 200),
        (1, 1,   30 / 200),
        (3, 1,   30 / 200),
        (-2, 2,  12 / 200),
        (0, 2,   26 / 200),
        (2, 2,   12 / 200),
        (-3, 3,   5 / 200),
        (-1, 3,  12 / 200),
        (1, 3,   12 / 200),
        (3, 3,    5 / 200)
    )
}


class BmpWriter(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(
            self, nInputPorts=1, inputType='vtkImageData')

        self._file_name = "default.bmp"
        self._dpm_array = [23623, 23623]

        self._split_img_bool = False
        self._x_img_size_limit = None
        self._margin_size = None

        self._f = None
        self._dithering = 'floyd-steinberg'

    def set_split_img_true(self, margin_size, x_limit):
        self._split_img_bool = True
        self._x_img_size_limit = x_limit
        self._margin_size = margin_size

    def set_split_img_false(self):
        self._split_img_bool = False

    def set_file_name(self, name):
        self._file_name = name

    def find_closest_color(self, old_val):

        if(old_val < 0):
            return 0
        elif(old_val > 255):
            return 255
        else:
            return round(old_val/255)*255

    def set_dpm(self, dpm_array):
        self._dpm_array = dpm_array

    def set_dithering(self, dithering):
        self._dithering = dithering.lower()

    def append_error(self, img, i, j, error):
        old_val = img.GetScalarComponentAsFloat(i, j, 0, 0)
        new_val = old_val + error

        img.SetScalarComponentFromFloat(i, j, 0, 0, new_val)

    def _init_file(self):
        self._f = open(self._file_name, 'wb')

    def _close_file(self):
        self._f.close()

    def _init_header(self, w, h, a_size):
        bmp_header_size = 14
        dib_header_size = 40
        rgb_color_table = 8

        a_offset = bmp_header_size + dib_header_size + rgb_color_table
        total_size = bmp_header_size + dib_header_size + a_size + rgb_color_table

        # BMP header
        self._f.write(pack('<HLHHL',
                           19778,
                           total_size,
                           0,
                           0,
                           a_offset))

        self._f.write(pack('<LllHHLLllLL',
                           dib_header_size,
                           w,
                           h,
                           1,
                           1,
                           0,
                           a_size,
                           self._dpm_array[0],
                           self._dpm_array[1],
                           0,
                           0))

        # RGBQUAD Array
        self._f.write(pack('<BBBB', 255, 255, 255, 0))
        self._f.write(pack('<BBBB', 0, 0, 0, 0))

    def dithering(self, img, i, j):
        old_val = img.GetScalarComponentAsFloat(i, j, 0, 0)
        new_val = self.find_closest_color(old_val)

        diffusion_map = _DIFFUSION_MAPS[self._dithering]

        extent = img.GetExtent()

        img.SetScalarComponentFromFloat(i, j, 0, 0, new_val)

        quant_error = old_val - new_val

        if(quant_error != 0):
            for dx, dy, ratio in diffusion_map:
                x = i + dx
                y = j + dy
                if (extent[0] <= x <= extent[1]) and (extent[2] <= y <= extent[3]):
                    self.append_error(img, x, y, ratio*quant_error)

        if(new_val == 255):
            return 0
        else:
            return 1

    def regular_print(self, inp):
        dim = inp.GetDimensions()

        # in bit
        line_size = dim[0]
        padding = 32 - dim[0] % 32

        # in bytes
        total_line_size = int((line_size + padding)/8)

        pixel_size = total_line_size*dim[1]

        self._init_header(dim[0], dim[1], pixel_size)

        extent = inp.GetExtent()
        # write image
        for j in range(extent[3], extent[2]-1, -1):
            bit_row = ""
            byte_array = bytearray(total_line_size)
            byte_array_loc = 0
            for i in range(extent[0], extent[1]+1):
                bit_row += str(self.dithering(inp, i, j))

                if(len(bit_row) == 8):
                    byte_array[byte_array_loc] = int(bit_row, base=2)
                    bit_row = ""
                    byte_array_loc += 1

            if(not bit_row):
                padding_8 = 8-len(bit_row) % 8
                bit_row += padding_8*"0"
                byte_array[byte_array_loc] = int(bit_row, base=2)
                byte_array_loc += 1

            self._f.write(byte_array)
    
    def dither_img(self, inp):
        dim = inp.GetDimensions()
        img = np.zeros(dim[0:2],dtype = int)
        for i in range(dim[0]):
            for j in range(dim[1]):
                img[i][j] = self.dithering(inp, i, j)
        return img

    def split_print(self, inp):
        img = self.dither_img(inp)

        dim = inp.GetDimensions()
        extent = inp.GetExtent()

        h_limit = self._x_img_size_limit - 2*self._margin_size
        number_of_slice = math.ceil(dim[1]/h_limit)
        new_img = None
        index_start = []
        for slice_num in range(number_of_slice):
            chunk = img[:][slice_num*h_limit:slice_num*h_limit+h_limit]
            if(np.sum(chunk) != 0):
                chunk_shape = np.shape(chunk)
                if(new_img is not None):
                    if(np.shape(new_img)[1] != np.shape(chunk)[1]):
                        left_over = h_limit - chunk_shape[1]
                        chunk = np.append(chunk, np.zeros((chunk_shape[0], left_over)), axis = 0)
                    new_img = np.concatenate((new_img, chunk), axis=1)
                else:
                    new_img = chunk
                index_start.append(slice_num*h_limit)
        
        number_sub_image = len(index_start)

        # in bit
        line_size = dim[0]*number_sub_image
        padding = 32 - line_size % 32

        # in bytes
        total_line_size = int((line_size + padding)/8)

        pixel_map_size = total_line_size*self._x_img_size_limit

        self._init_header(line_size, self._x_img_size_limit, pixel_map_size)

        "Pixel in bitmap are stored bottom-up"
        for j in reversed(range(self._x_img_size_limit)):
            # add margin
            if(j == h_limit - 1):
                empty_line = bytearray(total_line_size*self._margin_size)
                self._f.write(empty_line)

            bit_row = "".join(str(val) for val in new_img[:][j])
            bit_row.join("0"*padding)

            for k in range(len(bit_row)/8):
                self._f.write(pack('i', int(bit_row[8*k:8*k+8], 2)))

            if(j == extent[2]):
                empty_line = bytearray(total_line_size*self._margin_size)
                self._f.write(empty_line)

    def RequestData(self, request, inInfo, outInfo):
        inp = vtk.vtkImageData.GetData(inInfo[0])

        self._init_file()

        if(self._split_img_bool):
            self.split_print(inp)
        else:
            self.regular_print(inp)

        self._close_file()

        return 1
