from abc import ABC, abstractmethod
import vtk
from tempfile import TemporaryDirectory
import os
import shutil
from PIL import Image
from vtk.numpy_interface import dataset_adapter as dsa
import numpy as np

from typing import Callable, List

GcodeStep = Callable[[], str]


class GCodeWriter(ABC):

    def __init__(self) -> None:
        self.printer = None
        self.tmp_dir = TemporaryDirectory()
        self.filename = os.path.join(self.tmp_dir.name, 'toolpath.gcode')
        self.img_folder = os.path.join(self.tmp_dir.name, 'img')
        os.makedirs(self.img_folder, exist_ok=True)
        self.step = []

    @abstractmethod
    def home_axis(self, axis: np.array) -> GcodeStep:
        pass

    @abstractmethod
    def move(self, pos):
        pass

    @abstractmethod
    def initialise_printhead(self, printhead_num: int) -> GcodeStep:
        pass

    @abstractmethod
    def print_image(self, image: vtk.vtkImageData) -> GcodeStep:
        pass

    @abstractmethod
    def spit(self, print_head_num: int) -> GcodeStep:
        pass

    @abstractmethod
    def roller_start(self, rpm: float, ccw: bool = True) -> GcodeStep:
        pass

    @abstractmethod
    def roller_stop(self) -> GcodeStep:
        pass


BM_AXIS_MAP = ['X', 'Y']


class BigMachineGcode(GCodeWriter):

    def set_units(self, units: str) -> GcodeStep:
        unit_dict = {'metric': 'G21', 'imperial': 'G20'}
        return lambda: unit_dict[units] + '; Set Unit \n'

    def set_position_offset(self, pos: np.array) -> GcodeStep:
        def f():
            command = 'G92'
            for i, p in enumerate(pos):
                command += " %s%f" % (BM_AXIS_MAP[i], p)
            return command + '; Set Position Offset\n'

        return f

    def set_distance_mode(self, mode: str) -> GcodeStep:
        mode_dict = {'abs': 'G90', 'rel': 'G91'}
        return lambda: mode_dict[mode] + '; Set Distance mode\n'

    def move(self, pos: np.array) -> GcodeStep:
        """[summary]

        Args:
            pos (ndarray): array of position
        """
        def f() -> str:
            command = 'G1'
            for i, p in enumerate(pos):
                command += " %s%f" % (BM_AXIS_MAP[i], p)
            return command + '; Move axis \n'

        return f

    def move_feed_bed(self, pos: float, fb: int = 1, mode: str = 'rel') -> GcodeStep:
        def f() -> str:
            command = 'M203'
            mode_i = 0
            if mode == 'abs':
                mode_i = 1

            return command + ' F%i' % (fb) + ' T%f' % (pos) + ' A%i' % (mode_i) + ' ; Mode Feed bed \n'

        return f

    def move_build_bed(self, pos: float, bb: int = 1, mode: str = 'rel') -> GcodeStep:
        def f() -> str:
            command = 'M204'
            mode_i = 0
            if mode == 'abs':
                mode_i = 1

            return command + ' F%i' % (bb) + ' T%f' % (pos) + ' A%i' % (mode_i) + ' ; Mode Build bed \n'

        return f

    def home_axis(self, axis: np.array) -> GcodeStep:
        def f() -> str:
            command = ''
            for i in axis:
                command += ' %s' % i
            return 'G28' + command + '; home axis\n'

        return f

    def initialise_printhead(self, printhead_num: int) -> GcodeStep:
        return lambda: 'M6 P1 ; Select Imtech\nM93 P%i ; Initialize printhead\n' % (printhead_num)

    def print_image(self, img_name: str, img: vtk.vtkImageData,
                    z: int, printhead_num: int,
                    x: float, y: float, speed: float) -> GcodeStep:
        def f() -> str:
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

    def spit(self, printhead_num: int) -> GcodeStep:
        return lambda: "M95 P%i; spit printhead\n" % printhead_num

    def roller_start(self, rpm: float, ccw=True) -> GcodeStep:
        if ccw:
            return lambda: "M3 S%f; Roller start ccw\n" % rpm
        else:
            return lambda: "M4 S%f; Roller start cw\n" % rpm

    def roller_stop(self):
        return lambda: 'M3; Roller Stop\n'

    def export_file(self, path: str, ls_steps: List[GcodeStep]) -> None:
        with open(self.filename, mode='w') as f:
            for step in ls_steps:
                f.write(step())
        shutil.make_archive(path, 'zip', self.tmp_dir.name)
