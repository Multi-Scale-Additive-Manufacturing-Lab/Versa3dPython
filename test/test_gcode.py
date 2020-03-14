import unittest
from unittest import mock
import vtk

from versa3d.slicing import FullBlackSlicer
from versa3d.print_platter import PrintObject


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

        self._print_patch = mock.patch('versa3d.slicing.PrintSettings')

        type(self._print_patch).lt = mock.PropertyMock(return_value=0.1)

        self._printer_patch = mock.patch('versa3d.slicing.PrinterSettings')

        type(self._printer_patch).bds = mock.PropertyMock(return_value=[50.0,50.0,100.0])

        self._printhead_patch = mock.patch('versa3d.slicing.PrintheadSettings', dpi = [150,150])

        type(self._printhead_patch).dpi = mock.PropertyMock(return_value=[150,150])

        self._print_patch.start()
        self._printer_patch.start()
        self._printhead_patch.start()

    def test_generate_gcode(self):
        slicer = FullBlackSlicer(
            self.print_platter, 'default_settings', 'basic_printer', 'basic_printhead')

        slice_stack = slicer.slice()

        assert(len(slice_stack) != 0)

    def tearDown(self):
        self._print_patch.stop()
        self._printer_patch.stop()
        self._printhead_patch.stop()


if __name__ == '__main__':
    unittest.main()
