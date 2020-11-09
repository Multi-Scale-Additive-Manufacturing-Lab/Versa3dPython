import unittest
import numpy as np
import vtk
from collections import namedtuple
import os

from versa3d.slicing import FullBlackSlicer
from matplotlib import pyplot as plt


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

        bounds = reader.GetOutput().GetBounds()
        transform = vtk.vtkTransform()
        translate_vec = np.zeros(3)
        for i in range(3):
            if(bounds[2*i] < 0):
                translate_vec[i] = -bounds[2*i]*1.5
        
        transform.Translate(translate_vec)
        
        poly_translate = vtk.vtkTransformPolyDataFilter()
        poly_translate.SetTransform(transform)
        poly_translate.SetInputConnection(reader.GetOutputPort())
        poly_translate.Update()

        self.part = poly_translate.GetOutput()

        self.out_dir = './test/test_output/slicing'

        os.makedirs(self.out_dir, exist_ok=True)

    def test_slice_boat(self):
        slicer = FullBlackSlicer(self.part, self.print_setting(0.1), self.printer(
            np.array([50, 50, 100])), self.printhead(np.array([600, 600])))

        slice_stack = slicer.slice()
        self.assertTrue(len(slice_stack) > 0)

        mid_point = int(len(slice_stack)/2)
        vtk_im = slice_stack[mid_point].image
        rows, cols, _ = vtk_im.GetDimensions()

        writer = vtk.vtkBMPWriter()
        writer.SetInputData(vtk_im)
        writer.SetFileName(os.path.join(self.out_dir, 'test.bmp'))
        writer.Update()
        writer.Write()


if __name__ == '__main__':
    unittest.main()
