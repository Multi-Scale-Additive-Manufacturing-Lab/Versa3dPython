import unittest
from unittest import mock
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

        self.printer_obj = mock.Mock()
        self.printer_obj.build_bed_size.value = np.array(
            [100, 100], dtype=float)
        self.printer_obj.coord_offset.value = np.array([10, 10], dtype=float)
        self.printer_obj.gcode_flavour.value = 0

        self.print_param = mock.Mock()
        self.print_param.roller_rpm.value = 1000
        self.print_param.print_speed.value = 10.0
        self.print_param.tool_path_pattern.value = 0

        self.printhead = mock.Mock()

    def test_generate_gcode(self):
        slicer = ToolPathPlannerFilter()
        slicer.set_settings(self.printer_obj, self.printhead, self.print_param)

        slicer.SetInputDataObject(self.part)
        slicer.Update()

        slicer.write(self._output_path)


if __name__ == '__main__':
    unittest.main()
