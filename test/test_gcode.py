import unittest
from unittest import mock
import vtk

from versa3d.slicing import FullBlackSlicer
from versa3d.print_platter import PrintObject

from collections import namedtuple


def debug_setting():
    setting = namedtuple('PrinterSettings', 'name lt')
    return lambda name, lt = 0.1: setting(name, lt)


def debug_printer():
    setting = namedtuple('PrinterSettings', 'name bds')
    return lambda name, bds = [50.0, 50.0, 100.0]: setting(name, bds)


def debug_printhead():
    setting = namedtuple('PrintheadSettings', 'name dpi')
    return lambda name, dpi = [150.0, 150.0]: setting(name, dpi)


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

        self._print_patch = mock.patch(
            'versa3d.slicing.PrintSettings', new_callable=debug_setting)
        self._printer_patch = mock.patch(
            'versa3d.slicing.PrinterSettings', new_callable=debug_printer)
        self._printhead_patch = mock.patch(
            'versa3d.slicing.PrintheadSettings', new_callable=debug_printhead)

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
