from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from struct import pack
import vtk
import math


class BmpWriter(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(
            self, nInputPorts=1, inputType='vtkImageData')

        self._file_name = "default.bmp"
        self._dpm_array = [23622, 23622]

        self._split_img_bool = False
        self._x_img_size_limit = None
        self._margin_size = None

        self._f = None

    def set_split_img_true(self, margin_size, x_limit):
        self._split_img_bool = True
        self._x_img_size_limit = x_limit
        self._margin_size = margin_size

    def set_split_img_false(self):
        self._split_img_bool = False

    def set_file_name(self, name):
        self._file_name = name

    def find_closest_color(self, old_val):
        return round(old_val/255)*255

    def set_dpm(self, dpm_array):
        self._dpm_array = dpm_array

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

        a_offset = bmp_header_size + dib_header_size
        total_size = bmp_header_size + dib_header_size + a_size

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

        extent = img.GetExtent()

        img.SetScalarComponentFromFloat(i, j, 0, 0, new_val)

        quant_error = old_val-new_val

        if((i+1) <= extent[1] and quant_error != 0):
            self.append_error(img, i+1, j, quant_error*7/16)

        if ((i-1) >= extent[0] and (j+1) <= extent[3] and quant_error != 0):
            self.append_error(img, i-1, j, quant_error*3/16)

        if ((j+1) <= extent[3] and quant_error != 0):
            self.append_error(img, i, j+1, quant_error*5/16)

        if ((i+1) <= extent[1] and (j+1) <= extent[3] and quant_error != 0):
            self.append_error(img, i, j+1, quant_error*1/16)

        if(new_val == 255):
            return "0"
        else:
            return "1"

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
        for j in range(extent[2], extent[3]+1):
            bit_row = ""
            byte_array = bytearray(total_line_size)
            byte_array_loc = 0
            for i in range(extent[0], extent[1]+1):
                bit_row += self.dithering(inp, i, j)

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
    
    def split_print(self, inp):
        extent = inp.GetExtent()

        dim = inp.GetDimensions()
        extent = inp.GetExtent()

        h_limit = self._x_img_size_limit - 2*self._margin_size

        number_sub_image = math.ceil(dim[1]/h_limit)

        # in bit
        line_size = dim[0]*number_sub_image
        padding = 32 - line_size % 32

        # in bytes
        total_line_size = int((line_size + padding)/8)

        pixel_map_size = total_line_size*self._x_img_size_limit

        self._init_header(line_size, self._x_img_size_limit, pixel_map_size)

        for j in range(extent[2], h_limit):
            bit_row = ""
            byte_array = bytearray(total_line_size)
            byte_array_loc = 0
            
            #add margin
            if(j % h_limit):
                empty_line = bytearray(total_line_size*self._margin_size)
                self._f.write(empty_line)

            for i in range(extent[0],extent[0]+line_size):
                
                pseudo_j = j + h_limit*int(i/dim[0])
                
                #check to not go out of bound
                if(pseudo_j < dim[1]):
                    bit_row += self.dithering(inp, i%dim[0], j + h_limit*int(i/dim[0]))

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

    def RequestData(self, request, inInfo, outInfo):
        inp = vtk.vtkImageData.GetData(inInfo[0])

        self._init_file()

        if(self._split_img_bool):
            self.split_print(inp)
        else:
            self.regular_print(inp)

        self._close_file()

        return 1
