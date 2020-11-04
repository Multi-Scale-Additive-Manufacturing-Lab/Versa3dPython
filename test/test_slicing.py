import unittest
import numpy as np
import vtk
from collections import namedtuple

from versa3d.slicing import FullBlackSlicer


class SlicingTest(unittest.TestCase):

    def setUp(self):
        reader = vtk.vtkSTLReader()
        reader.SetFileName('./test/test_file/3DBenchySmall.stl')
        reader.Update()

        self.printer = namedtuple(
            'printer',
            ['build_bed_size']
        )

        self.print_setting = namedtuple(
            'parameter_preset',
            ['layer_thickness']
        )

        self.printhead = namedtuple(
            'printhead',
            ['dpi']
        )

        self.part = reader.GetOutput()

    def test_slice_boat(self):
        slicer = FullBlackSlicer(self.part, self.print_setting(0.1), self.printer(
            np.array([100, 100, 100])), self.printhead(np.array([60, 60])))

        slice_stack = slicer.slice()
        self.assertTrue(len(slice_stack) > 0)


if __name__ == '__main__':
    unittest.main()
