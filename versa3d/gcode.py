from abc import ABC, abstractmethod
import vtk
from tempfile import TemporaryDirectory
import os
import shutil

class GCodeWriter(ABC):

    def __init__(self):
        self.printer = None
        self.tmp_dir = TemporaryDirectory()
        self.filename = os.path.join(self.tmp_dir, 'toolpath.gcode')
        self.img_folder = os.path.join(self.tmp_dir,'img')
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

BM_AXIS_MAP = {
    1: 'X',
    2: 'Y',
    3: 'Z',
    4: 'T'
}


class BigMachineGcode(GCodeWriter):

    def set_units(self, units):
        unit_dict = {'metric': 'G21', 'imperial' : 'G20'}
        return lambda : unit_dict[units]

    def set_position_offset(self, pos):
        def f():
            command = 'G92'
            for i, p in enumerate(pos):
                if p != 0:
                    command += ' {%s}{%f}'.format(BM_AXIS_MAP[i], p)
            return command + '\n'

        return f 

    def set_distance_mode(self, mode):
        mode_dict = {'abs' : 'G90', 'rel' : 'G91'}
        return lambda : mode_dict[mode] + '\n'

    def move(self, pos):
        """[summary]

        Args:
            pos (ndarray): array of position
        """
        def f():
            command = 'G0'
            for i, p in enumerate(pos):
                if p != 0:
                    command += ' {%s}{%f}'.format(BM_AXIS_MAP[i], p)
            return command + '\n'

        return f

    def home_axis(self, axis):
        def f():
            command = ''
            for i in axis:
                command += ' {%s}'.format(i)
            return 'G28' + command + '\n'

        return f

    def initialise_printhead(self, printhead_num):
        def f():
            return 'M93 P{%i}\n'.format(printhead_num)

        return f

    def print_image(self, img_name, img, printhead_num, x, y, speed):
        def f():

            im_writer = vtk.vtkBMPWriter()
            im_writer.SetFileName(os.path.join(self.img_folder, img_name))
            im_writer.SetInputData(img)
            im_writer.Update()
            im_writer.Write()
            return 'M95 P{%i} X{%f} Y{%f} S{%f}\n'.format(printhead_num, x, y, speed)

        return f

    def spit(self, printhead_num):
        def f():
            return 'M95 P{%i}\n'.format(printhead_num)

        return f

    def roller_start(self, rpm, ccw=True):
        if ccw:
            return lambda: 'M3 S{%f}\n'.format(rpm)
        else:
            return lambda: 'M4 S{%f}\n'.format(rpm)
    
    def roller_stop(self):
        return 'M3\n'

    def export_file(self, path, ls_steps):
        with open(self.filename, mode = 'w') as f:
            for step in ls_steps:
                f.write(step())
        shutil.make_archive(path, 'zip', self.tmp_dir)

            