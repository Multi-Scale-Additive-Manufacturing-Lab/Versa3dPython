from abc import ABC, abstractmethod
import vtk
from tempfile import TemporaryDirectory
import os
import shutil
from PIL import Image
from vtk.numpy_interface import dataset_adapter as dsa
import numpy as np


class GCodeWriter(ABC):

    def __init__(self):
        self.printer = None
        self.tmp_dir = TemporaryDirectory()
        self.filename = os.path.join(self.tmp_dir.name, 'toolpath.gcode')
        self.img_folder = os.path.join(self.tmp_dir.name, 'img')
        os.makedirs(self.img_folder, exist_ok=True)
        self.step = []

    @abstractmethod
    def home_axis(self, axis):
        pass

    @abstractmethod
    def move(self, pos):
        pass

    @abstractmethod
    def initialise_printhead(self, print_head_num):
        pass

    @abstractmethod
    def print_image(self, image):
        pass

    @abstractmethod
    def spit(self, print_head_num):
        pass

    @abstractmethod
    def roller_start(self, rpm, ccw=True):
        pass

    @abstractmethod
    def roller_stop(self):
        pass


BM_AXIS_MAP = ['X', 'Y']


class BigMachineGcode(GCodeWriter):

    def set_units(self, units):
        unit_dict = {'metric': 'G21', 'imperial': 'G20'}
        return lambda: unit_dict[units] + '; Set Unit \n'

    def set_position_offset(self, pos):
        def f():
            command = 'G92'
            for i, p in enumerate(pos):
                command += " %s%f" % (BM_AXIS_MAP[i], p)
            return command + '; Set Position Offset\n'

        return f

    def set_distance_mode(self, mode):
        mode_dict = {'abs': 'G90', 'rel': 'G91'}
        return lambda: mode_dict[mode] + '; Set Distance mode\n'

    def move(self, pos):
        """[summary]

        Args:
            pos (ndarray): array of position
        """
        def f():
            command = 'G1'
            for i, p in enumerate(pos):
                command += " %s%f" % (BM_AXIS_MAP[i], p)
            return command + '; Move axis \n'

        return f

    def move_feed_bed(self, pos, fb=1, mode='rel'):
        def f():
            command = 'M203'
            mode_i = 0
            if mode == 'abs':
                mode_i = 1

            return command + ' F%i' % (fb) + ' T%f' % (pos) + ' A%i' % (mode_i) + ' ; Mode Feed bed \n'

        return f

    def move_build_bed(self, pos, bb=1, mode='rel'):
        def f():
            command = 'M204'
            mode_i = 0
            if mode == 'abs':
                mode_i = 1

            return command + ' F%i' % (bb) + ' T%f' % (pos) + ' A%i' % (mode_i) + ' ; Mode Build bed \n'

        return f

    def home_axis(self, axis):
        def f():
            command = ''
            for i in axis:
                command += ' %s' % i
            return 'G28' + command + '; home axis\n'

        return f

    def initialise_printhead(self, printhead_num):
        return lambda: 'M6 P1 ; Select Imtech\nM93 P%i ; Initialize printhead\n' % (printhead_num)

    def print_image(self, img_name, img, z, printhead_num, x, y, speed):
        def f():
            x_d, y_d, _ = img.GetDimensions()
            single_slice = vtk.vtkExtractVOI()
            single_slice.SetSampleRate([1, 1, 1])
            single_slice.SetInputData(img)
            single_slice.SetVOI(0, x_d - 1, 0, y_d - 1, z, z)
            single_slice.Update()

            image = dsa.WrapDataObject(single_slice.GetOutput())
            point_data = image.PointData['ImageScalars'].reshape(
                image.GetDimensions()[0:2], order='F').T
            pil_im = Image.fromarray(point_data)
            pil_im.convert('1')
            pil_im.save(os.path.join(self.img_folder, img_name))

            return "M95 P%i I%i X%f Y%f S%f; Print layer\n" % (printhead_num, z, x, y, speed)

        return f

    def spit(self, printhead_num):
        return lambda: "M95 P%i; spit printhead\n" % printhead_num

    def roller_start(self, rpm, ccw=True):
        if ccw:
            return lambda: "M3 S%f; Roller start ccw\n" % rpm
        else:
            return lambda: "M4 S%f; Roller start cw\n" % rpm

    def roller_stop(self):
        return lambda: 'M3; Roller Stop\n'

    def export_file(self, path, ls_steps):
        with open(self.filename, mode='w') as f:
            for step in ls_steps:
                f.write(step())
        shutil.make_archive(path, 'zip', self.tmp_dir.name)
