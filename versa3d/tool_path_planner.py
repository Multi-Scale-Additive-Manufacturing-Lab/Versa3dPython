import os
from versa3d.gcode import BigMachineGcode, GCodeWriter, GcodeStep
from abc import ABC, abstractmethod
from vtkmodules.vtkCommonDataModel import vtkImageData
from vtkmodules.util.vtkConstants import VTK_UNSIGNED_CHAR
from vtkmodules.numpy_interface import dataset_adapter as dsa
import numpy as np

from versa3d.settings import PrintSetting, BinderJettingPrintParameter, BinderJettingPrinter, GenericPrinter, PixelPrinthead
# from versa3d.print_platter import PrintObject
import versa3d.util as vutil
from typing import Callable, List, Any, Tuple

GCODE_FLAVOUR = {
    0: BigMachineGcode
}


GenericToolPathPlanner = Callable[[GCodeWriter, List['PrintObject'],
                                   GenericPrinter,
                                   PixelPrinthead,
                                   BinderJettingPrintParameter], List[GcodeStep]]


class GenericToolPathPlanner(ABC):
    @abstractmethod
    def export(self, gcode_writer: BigMachineGcode,
               ls_obj: List['PrintObject'],
               printer: GenericPrinter,
               printhead: PixelPrinthead,
               param: BinderJettingPrintParameter) -> List[GcodeStep]:
        raise(NotImplementedError)


class BinderJettingToolPath(GenericToolPathPlanner):

    def merge_image(self, build_dim: np.ndarray, spacing: np.ndarray, ls_obj: List['PrintObject']) -> Tuple[vtkImageData, int]:

        bg_im = vtkImageData()
        bg_im.SetSpacing(spacing)
        bg_im.SetDimensions(build_dim)
        bg_im.SetOrigin(0, 0, 0)
        bg_im.AllocateScalars(VTK_UNSIGNED_CHAR, 1)
        bg_im.GetPointData().GetScalars().Fill(255)

        w_bg = dsa.WrapDataObject(bg_im)
        data_bg = np.reshape(
            w_bg.PointData['ImageScalars'], build_dim, order='F')

        top_layer = 0

        for obj in ls_obj:
            vtk_im = dsa.WrapDataObject(obj.sliced_object)
            origin = np.ceil(np.array(vtk_im.GetOrigin())/spacing).astype(int)
            obj_dim = np.array(vtk_im.GetDimensions()).astype(int)
            top_z = origin[2] + obj_dim[2]
            obj_data = np.reshape(
                vtk_im.PointData['ImageScalars'], obj_dim, order='F')
            data_bg[origin[0]:origin[0] + obj_dim[0],
                    origin[1]:origin[1] + obj_dim[1],
                    origin[2]:top_z] = obj_data

            if(top_z > top_layer):
                top_layer = top_z

        return bg_im, top_layer

    def export(self, gcode_writer: BigMachineGcode,
               ls_obj: List['PrintObject'],
               printer: GenericPrinter,
               printhead: PixelPrinthead,
               param: BinderJettingPrintParameter) -> List[GcodeStep]:

        res = printhead.dpi.value
        layer_thickness = param.layer_thickness.value
        build_bed_size = printer.build_bed_size.value
        spacing = vutil.compute_spacing(layer_thickness, res)

        coord_offset = printer.coord_offset.value
        roller_rpm = param.roller_rpm.value
        print_speed = param.print_speed.value

        build_dim = np.ceil(build_bed_size / spacing).astype(int)
        vtk_im, top_layer = self.merge_image(build_dim, spacing, ls_obj)

        ls_step = []
        ls_step.append(gcode_writer.set_units('metric'))
        ls_step.append(gcode_writer.home_axis(['X', 'Y', 'Z', 'U']))

        ls_step.append(gcode_writer.set_position_offset(coord_offset))
        ls_step.append(gcode_writer.initialise_printhead(1))

        for z in range(top_layer):
            ls_step.append(gcode_writer.move([0, 0]))
            ls_step.append(gcode_writer.roller_start(1, roller_rpm))

            ls_step.append(gcode_writer.move_feed_bed(layer_thickness))
            ls_step.append(gcode_writer.move_build_bed(layer_thickness))

            ls_step.append(gcode_writer.move([0, build_bed_size[1]]))

            ls_step.append(gcode_writer.print_image(
                'img_{}.bmp'.format(z), vtk_im, z, 1, 0, 0, print_speed))

            ls_step.append(gcode_writer.roller_stop())

        return ls_step


TOOL_PATH_NAME = {
    0: BinderJettingToolPath
}


class ToolPathPlannerFilter():
    def __init__(self) -> None:
        self.gcode_writer = None
        self._gcode_flavour = None

        self._tool_path_pattern = None
        self.step_generator = None

        self._steps = None

        self._printer = None
        self._printhead = None
        self._param = None

    @property
    def printer(self) -> GenericPrinter:
        return self._printer

    @property
    def printhead(self) -> PixelPrinthead:
        return self._printhead

    @property
    def print_parameter(self) -> BinderJettingPrintParameter:
        return self._param

    @printer.setter
    def printer(self, setting: GenericPrinter) -> None:
        self._gcode_flavour = setting.gcode_flavour.value
        self.gcode_writer = GCODE_FLAVOUR[self._gcode_flavour]()
        self._printer = setting

    @printhead.setter
    def printhead(self, setting: PixelPrinthead):
        self._printhead = setting

    @print_parameter.setter
    def print_parameter(self, setting: BinderJettingPrintParameter) -> None:
        self._tool_path_pattern = setting.tool_path_pattern.value
        self.step_generator = TOOL_PATH_NAME[self._tool_path_pattern]()
        self._param = setting

    def write(self, file_path: str, ls_obj: List['PrintObject'],
              printer: GenericPrinter,
              printhead: PixelPrinthead,
              param: BinderJettingPrintParameter) -> None:
        # TODO change to something more flexible, duplication of zip extension
        s_fp = os.path.splitext(file_path)[0]

        self.printer = printer
        self.printhead = printhead
        self.print_parameter = param

        self._steps = self.step_generator.export(
            self.gcode_writer, ls_obj, self.printer, self.printhead, self.print_parameter)
        self.gcode_writer.export_file(s_fp, self._steps)
