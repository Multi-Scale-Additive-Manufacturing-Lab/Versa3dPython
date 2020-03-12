import unittest
import os

import vtk


class gcode_test(unittest.TestCase):

    def setUp(self):

        reader = vtk.vtkSTLReader()
        reader.SetFileName('./test/test_file/3DBenchySmall.stl')
        reader.Update()

        self.polydata = reader.GetOutput()

        printbedsize = [50,50,100]

    def test_generate_gcode(self):
        assert(False)
        print('done')