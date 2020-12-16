import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from versa3d.gcode import BigMachineGcode
from abc import ABC, abstractmethod

import numpy as np

GCODE_FLAVOUR = {
    0 : BigMachineGcode
}

class GenericToolPathPlanner(ABC):
    @abstractmethod
    def update_printhead(self, setting):
        pass

    @abstractmethod
    def update_printer(self, setting):
        pass

    @abstractmethod
    def update_param(self, setting):
        pass

    @abstractmethod
    def generate_step(self, gcode_writer, image):
        pass


class BinderJettingPlanner(GenericToolPathPlanner):
    def __init__(self):
        super().__init__()
        self._build_bed_size = np.array([100,100,300], dtype = float)
        self._coord_offset = np.array([100,100], dtype = float)

        self._roller_rpm = 200.0
        self._print_speed = 10.0

    def update_printhead(self, setting):
        return False
    
    def update_param(self, setting):
        if not ('roller_rpm' in setting and 'print_speed' in setting):
            raise ValueError
        modified = False
        if self._roller_rpm != setting['roller_rpm'].value:
            self._roller_rpm = setting['roller_rpm'].value
            modified = True
        
        if self._print_speed != setting['print_speed'].value:
            self._print_speed = setting['print_speed'].value
            modified = True
        
        return modified

    def update_printer(self, setting):
        if not ('build_bed_size' in setting and 'coord_offset' in setting):
            raise ValueError
        modified = False
        if np.any(self._build_bed_size != setting['build_bed_size'].value):
            self._build_bed_size = setting['build_bed_size'].value
            modified = True
        
        if np.any(self._coord_offset != setting['coord_offset'].value):
            self._coord_offset = setting['coord_offset'].value
            modified = True
        
        return modified

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
            ls_step.append(gcode_writer.move([0, 0]))
            ls_step.append(gcode_writer.roller_start(1, self._roller_rpm))
            
            ls_step.append(gcode_writer.move_feed_bed(z_spacing))
            ls_step.append(gcode_writer.move_build_bed( z_spacing))

            ls_step.append(gcode_writer.move([0, self._build_bed_size[1]]))

            ls_step.append(gcode_writer.print_image(
                'img_{}.bmp'.format(z), image, z, 1, origin[0], origin[1], self._print_speed))

            ls_step.append(gcode_writer.roller_stop())

        return ls_step


TOOL_PATH_NAME = {
    0: BinderJettingPlanner
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
    
    def set_settings(self, printer, printhead, print_param):
        self.set_printer(printer)
        self.set_print_parameter(print_param)
        self.set_printhead(printhead)

    def set_printer(self, setting):
        if setting['gcode_flavour'].value != self._gcode_flavour:
            self.Modified()
            self._gcode_flavour = setting['gcode_flavour'].value
            self.gcode_writer = GCODE_FLAVOUR[self._gcode_flavour]()
    
    def set_printhead(self, setting):
        if self.step_generator.update_printhead(setting):
            self.Modified()
    
    def set_print_parameter(self, setting):
        if setting['tool_path_pattern'].value != self._tool_path_pattern:
            self.Modified()
            self._tool_path_pattern = setting['tool_path_pattern'].value
            self.step_generator = TOOL_PATH_NAME[self._tool_path_pattern]()

        if self.step_generator.update_param(setting):
            self.Modified()

    def RequestData(self, request, inInfo, outInfo):
        img_stack = vtk.vtkImageData.GetData(inInfo[0])
        self._steps = self.step_generator.generate_step(
            self.gcode_writer, img_stack)
        return 1

    def write(self, file_path):
        self.gcode_writer.export_file(file_path, self._steps)
