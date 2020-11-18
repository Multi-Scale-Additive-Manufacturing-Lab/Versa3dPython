import numpy as np
import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtk.numpy_interface import dataset_adapter as dsa
from versa3d.gcode import BigMachineGcode
import zipfile as zf

GCODE_FLAVOUR = {
    'BigMachine' : BigMachineGcode
}

TOOL_PATH_NAME = {
    'StandardBinderJetting' : binder_jetting_standard_step
}

def binder_jetting_standard_step(tool_path_planner, image):
    gcode_writer = tool_path_planner._gcode_writer
    z_spacing = image.GetSpacing()[2]
    x_d, y_d, z_d = image.GetDimensions()

    single_slice = vtk.vtkExtractVOI()
    single_slice.SetSampleRate([1,1,1])
    single_slice.SetInputData(image)

    ls_step = []

    for i in range(4):
        ls_step.append(gcode_writer.home_axis(i))

    ls_step.append(gcode_writer.set_position_offset([30,30]))
    ls_step.append(gcode_writer.initialise_printhead(1))

    for z in range(z_d):
        ls_step.append(gcode_writer.set_distance_mode('abs'))
        ls_step.append(gcode_writer.roller_start(1, 200))
        
        ls_step.append(gcode_writer.set_distance_mode('rel'))
        ls_step.append(gcode_writer.move([0,0,z_spacing,0]))
        ls_step.append(gcode_writer.move([0,0,0,z_spacing]))

        ls_step.append(gcode_writer.set_distance_mode('abs'))
        ls_step.append(gcode_writer.move(1, 200))

        single_slice.SetVOI(0, x_d,0, y_d, z, z)
        single_slice.Update()

        ls_step.append(gcode_writer.print_image('img_{}'.format(z), single_slice.GetOutput(),1, 0, 0, 30))

        ls_step.append(gcode_writer.roller_stop())
    
    return ls_step


class ToolPathPlanner(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self,
                                        nInputPorts=1, inputType='vtkImageData',
                                        nOutputPorts=0)
        self.gcode_writer = None
        self._gcode_flavour = None

        self._tool_path_pattern = None
        self.step_generator = None

        self._steps = None
    
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
            self.step_generator = TOOL_PATH_NAME[val]
    
    def RequestData(self, request, inInfo, outInfo):
        img_stack = vtk.vtkImageData.GetData(inInfo[0])
        self._steps = self.step_generator(self, img_stack)
        return 1
    
    def write(self, path):
        with open(path,mode = 'w') as f:
            for step in self._steps:
                f.write(step())

