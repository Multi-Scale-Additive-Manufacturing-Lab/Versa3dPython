import unittest
from collections import namedtuple
import vtk
import numpy as np

from versa3d.tool_path_planner import ToolPathPlannerFilter


class GcodeTest(unittest.TestCase):

    def setUp(self):
        reader = vtk.vtkXMLImageDataReader()
        reader.SetFileName('./test/test_file/3DBenchySmall.vti')
        reader.Update()

        self.part = reader.GetOutput()

        self._output_path = './test/test_output/gcode_output'

        self.PrinterObj = namedtuple('printer', ['build_bed_size'])
        self.ParamObj = namedtuple(
            'parameter_preset', ['roller_rpm', 'print_speed'])

    def test_generate_gcode(self):
        slicer = ToolPathPlannerFilter()

        slicer.gcode_flavour = 'BigMachine'
        slicer.tool_path_pattern = 'StandardBinderJetting'

        slicer.printer = self.PrinterObj(np.array([100, 100], dtype=float))
        slicer.param = self.ParamObj(100, 20)

        slicer.SetInputDataObject(self.part)
        slicer.Update()

        slicer.write(self._output_path)


if __name__ == '__main__':
    unittest.main()
