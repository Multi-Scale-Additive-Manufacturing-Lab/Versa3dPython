import unittest
import vtk

from src.slicing import FullBlackSlicer


class gcode_test(unittest.TestCase):

    def setUp(self):

        reader = vtk.vtkSTLReader()
        reader.SetFileName('./test/test_file/3DBenchySmall.stl')
        reader.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        self.actor = vtk.vtkActor()
        self.actor.SetMapper(mapper)

    def test_generate_gcode(self):
        printer_bounds = [50, 50, 100]
        layer_thickness = 0.1
        dpi = [150, 150]

        slicer = FullBlackSlicer(printer_bounds, layer_thickness, dpi)
        slicer.add_actor(self.actor)

        slice_stack = slicer.slice()

        assert(len(slice_stack) != 0)
