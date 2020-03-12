import unittest
import os
from unittest.mock import Mock

import vtk


class gcode_test(unittest.TestCase):

    def setUp(self):

        reader = vtk.vtkSTLReader()
        reader.SetFileName('./test/test_file/3DBenchySmall.stl')
        reader.Update()

        printbedsize = [50, 50, 100]

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        self.actor = vtk.vtkActor()
        self.actor.SetMapper(mapper)

        print_platter = Mock()

    def test_generate_gcode(self):
        assert(False)
        print('done')
