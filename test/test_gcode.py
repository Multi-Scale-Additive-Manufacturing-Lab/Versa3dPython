import unittest
from unittest import mock
import vtk

from src.slicing import FullBlackSlicer
from src.print_platter import PrintObject


class GcodeTest(unittest.TestCase):

    def setUp(self):

        reader = vtk.vtkSTLReader()
        reader.SetFileName('./test/test_file/3DBenchySmall.stl')
        reader.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        print_obj = PrintObject('test obj', actor)

        self.print_platter = mock.MagicMock(parts=[print_obj])

    @mock.patch('slicing.PrinterSettings')
    @mock.patch('slicing.PrintheadSettings')
    @mock.patch('slicing.PrintSettings')
    def test_generate_gcode(self, mock_print, mock_printhead, mock_printer):

        layer_thickness = mock.PropertyMock(return_value=0.1)
        type(mock_print).lt = layer_thickness

        dpi = mock.PropertyMock(return_value=[150, 150])
        type(mock_printhead).dpi = dpi

        printer_size = mock.PropertyMock(return_value=[50.0, 50.0, 100.0])
        type(mock_printer).bds = printer_size

        slicer = FullBlackSlicer(
            self.print_platter, 'default_settings', 'basic_printer', 'basic_printhead')

        slice_stack = slicer.slice()

        assert(len(slice_stack) != 0)


if __name__ == '__main__':
    unittest.main()
