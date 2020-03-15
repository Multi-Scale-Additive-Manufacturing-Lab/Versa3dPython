import unittest
from unittest import mock
import vtk

from versa3d.slicing import FullBlackSlicer
from versa3d.print_platter import PrintObject
from versa3d.gcode import LinuxCncWriter

from collections import namedtuple


class DebugSetting():
    def __init__(self, lt, rot_rol, rot_lin, h, s, w, fbv, bbv, ps):
        self._lt = lt
        self._rot_rol = rot_rol
        self._rot_lin = rot_lin
        self._h = h
        self._s = s
        self._w = w
        self._fbv = fbv
        self._bbv = bbv
        self._ps = ps

    def __call__(self, name=None):
        setting = namedtuple('PrinterSettings', [
                             'name', 'lt', 'rol_lin', 'rol_rpm', 'bbv', 'fbv', 'rwd', 'pl', 'pho', 'ps'])
        return setting(name, self._lt, self._rot_lin, self._rot_rol, self._bbv, self._fbv, self._w, self._s, self._h, self._ps)


class DebugPrinter():
    def __init__(self, bds, coord_o):
        self._bds = bds
        self._coord_o = coord_o

    def __call__(self, name=None):
        setting = namedtuple('PrinterSettings', 'name bds coord_o')
        return setting(name, self._bds, self._coord_o)


class DebugPrinthead():
    def __init__(self, dpi):
        self._dpi = dpi

    def __call__(self, name=None):
        setting = namedtuple('PrintheadSettings', 'name dpi')
        return setting(name, self._dpi)


class GcodeTest(unittest.TestCase):

    def setUp(self):

        reader = vtk.vtkSTLReader()
        reader.SetFileName('./test/test_file/3DBenchySmall.stl')
        reader.Update()

        self._output_path = './test/test_output'

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        z_range = actor.GetZRange()

        new_pos = [0]*3

        old_pos = actor.GetPosition()

        bds = [50.0, 50.0, 100.0]

        new_pos[0] = bds[0]/2
        new_pos[1] = bds[1]/2

        if(z_range[0] < 0):
            new_pos[2] = old_pos[2]-z_range[0]
        else:
            new_pos[2] = old_pos[2]

        actor.SetPosition(new_pos)
        actor.RotateZ(45)

        print_obj = PrintObject('test obj', actor)

        self.print_platter = mock.MagicMock(parts=[print_obj])

        def debug_setting(): return DebugSetting(
            0.1, 360.0, 10.0, 0.1, 0.2, 0.1, 1.0, 1.0, 1.0)

        def debug_printer(): return DebugPrinter(
            [50.0, 50.0, 100.0], [0.0, 0.0])

        def debug_printhead(): return DebugPrinthead([150, 150])

        self._print_patch_slicing = mock.patch(
            'versa3d.slicing.PrintSettings', new_callable=debug_setting)
        self._printer_patch_slicing = mock.patch(
            'versa3d.slicing.PrinterSettings', new_callable=debug_printer)
        self._printhead_patch_slicing = mock.patch(
            'versa3d.slicing.PrintheadSettings', new_callable=debug_printhead)

        self._print_patch_slicing.start()
        self._printer_patch_slicing.start()
        self._printhead_patch_slicing.start()

        self._print_patch_gcode = mock.patch(
            'versa3d.gcode.PrintSettings', new_callable=debug_setting)
        self._printer_patch_gcode = mock.patch(
            'versa3d.gcode.PrinterSettings', new_callable=debug_printer)
        self._printhead_patch_gcode = mock.patch(
            'versa3d.gcode.PrintheadSettings', new_callable=debug_printhead)

        self._print_patch_gcode.start()
        self._printer_patch_gcode.start()
        self._printhead_patch_gcode.start()

    def test_generate_gcode(self):
        slicer = FullBlackSlicer(
            self.print_platter, 'default_settings', 'basic_printer', 'basic_printhead')

        slice_stack = slicer.slice()

        writer = LinuxCncWriter(slicer, 'default_settings', 'basic_printer')

        assert(len(slice_stack) != 0)

        writer.write_file(self._output_path)

    def tearDown(self):
        self._print_patch_slicing.stop()
        self._printer_patch_slicing.stop()
        self._printhead_patch_slicing.stop()

        self._print_patch_gcode.stop()
        self._printer_patch_gcode.stop()
        self._printhead_patch_gcode.stop()


if __name__ == '__main__':
    unittest.main()
