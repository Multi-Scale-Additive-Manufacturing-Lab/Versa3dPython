import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from versa3d.gcode import BigMachineGcode
from abc import ABC, abstractmethod

import numpy as np

GCODE_FLAVOUR = {
    'BigMachine': BigMachineGcode
}


class GenericToolPathPlanner(ABC):
    def __init__(self):
        self._printhead = None
        self._printer = None
        self._param = None

    @abstractmethod
    def update_printhead(self, planner, printhead):
        pass

    @abstractmethod
    def update_printer(self, planner, printer):
        pass

    @abstractmethod
    def update_param(self, planner, param):
        pass

    @abstractmethod
    def generate_step(self, gcode_writer, image):
        pass


class BinderJettingPlanner(GenericToolPathPlanner):
    def __init__(self):
        super().__init__()
        self._build_bed_size = None
        self._coord_offset = None

        self._roller_rpm = None
        self._print_speed = None

    def update_printhead(self, planner, printhead):
        self._printhead = printhead

    def update_param(self, planner, param):
        if self._param is None and param:
            planner.Modified()
            self._param = param
            self._roller_rpm = param.roller_rpm
            self._print_speed = param.print_speed
        elif self._param and param:
            if self._roller_rpm != param.roller_rpm:
                planner.Modified()
                self._roller_rpm = param.roller_rpm
            if self._print_speed != param.print_speed:
                planner.Modified()
                self._print_speed = param.print_speed

    def update_printer(self, planner, printer):
        if self._printer is None and printer:
            planner.Modified()
            self._printer = printer
            self._build_bed_size = printer.build_bed_size
            self._coord_offset = printer.coord_offset
        elif self._printer and printer:
            if np.any(self._build_bed_size != printer.build_bed_size):
                planner.Modified()
                self._build_bed_size = printer.build_bed_size
            elif np.any(self._coord_offset != printer.coord_offset):
                planner.Modified()
                self._coord_offset = printer.coord_offset

    def generate_step(self, gcode_writer, image):
        z_spacing = image.GetSpacing()[2]
        z_d = image.GetDimensions()[2]
        origin = np.array(image.GetOrigin())

        ls_step = []
        ls_step.append(gcode_writer.set_units('metric'))
        ls_step.append(gcode_writer.home_axis(['X', 'Y', 'Z', 'U']))

        ls_step.append(gcode_writer.set_position_offset(self._coord_offset))
        ls_step.append(gcode_writer.initialise_printhead(1))

        for z in range(z_d):
            ls_step.append(gcode_writer.move([0, 0, 0, 0]))
            ls_step.append(gcode_writer.set_distance_mode('abs'))
            ls_step.append(gcode_writer.roller_start(1, self._roller_rpm))

            ls_step.append(gcode_writer.set_distance_mode('rel'))
            ls_step.append(gcode_writer.move([0, 0, z_spacing, 0]))
            ls_step.append(gcode_writer.move([0, 0, 0, z_spacing]))

            ls_step.append(gcode_writer.set_distance_mode('abs'))
            ls_step.append(gcode_writer.move([0, self._build_bed_size[1], 0, 0]))

            ls_step.append(gcode_writer.print_image(
                'img_{}.bmp'.format(z), image, z, 1, origin[0], origin[1], self._print_speed))

            ls_step.append(gcode_writer.roller_stop())

        return ls_step


TOOL_PATH_NAME = {
    'StandardBinderJetting': BinderJettingPlanner
}


class ToolPathPlannerFilter(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self,
                                        nInputPorts=1, inputType='vtkImageData',
                                        nOutputPorts=0)
        self.gcode_writer = None
        self._gcode_flavour = None

        self._tool_path_pattern = None
        self.step_generator = None

        self._steps = None

        self._printer = None
        self._printhead = None
        self._param = None

    @property
    def gcode_flavour(self):
        return self._gcode_flavour

    @gcode_flavour.setter
    def gcode_flavour(self, val):
        if val != self._gcode_flavour:
            self.Modified()
            self._gcode_flavour = val
            self.gcode_writer = GCODE_FLAVOUR[val]()

    @property
    def tool_path_pattern(self):
        return self._tool_path_pattern

    @tool_path_pattern.setter
    def tool_path_pattern(self, val):
        if val != self._tool_path_pattern:
            self.Modified()
            self._tool_path_pattern = val
            self.step_generator = TOOL_PATH_NAME[val]()

    @property
    def printer(self):
        return self._printer

    @printer.setter
    def printer(self, val):
        if val != self._printer:
            self.step_generator.update_printer(self, val)
            self._printer = val

    @property
    def printhead(self):
        return self._printhead

    @printhead.setter
    def printhead(self, val):
        if val != self._printhead:
            self.step_generator.update_printhead(self, val)
            self._printhead = val

    @property
    def param(self):
        return self._param

    @param.setter
    def param(self, val):
        if val != self.param:
            self.step_generator.update_param(self, val)
            self._param = val

    def RequestData(self, request, inInfo, outInfo):
        img_stack = vtk.vtkImageData.GetData(inInfo[0])
        self._steps = self.step_generator.generate_step(
            self.gcode_writer, img_stack)
        return 1

    def write(self, path):
        self.gcode_writer.export_file(path, self._steps)
