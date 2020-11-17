import unittest
import numpy as np
import vtk
import os

from versa3d.slicing import VoxelSlicer

from test.util import render_image


class SlicingTest(unittest.TestCase):

    def setUp(self):
        reader = vtk.vtkSTLReader()
        reader.SetFileName('./test/test_file/3DBenchySmall.stl')
        reader.Update()

        self.resolution = np.array([600, 600])
        self.layer_thickness = 0.1

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
        slicer = VoxelSlicer()
        slicer.resolution = self.resolution
        slicer.layer_thickness = self.layer_thickness
        slicer.SetInputDataObject(self.part)
        slicer.Update()

        slice_stack = slicer.GetOutputDataObject(0)
        img_dim = slice_stack.GetDimensions()
        self.assertTrue(img_dim[2] > 0)
        (x_min, x_max, y_min, y_max, _, _) = slice_stack.GetExtent()

        mid_point = int(img_dim[2]/2)
        single_im = vtk.vtkExtractVOI()
        single_im.SetVOI(x_min, x_max, y_min, y_max, mid_point, mid_point)
        single_im.SetSampleRate(1, 1, 1)
        single_im.SetInputData(slice_stack)
        single_im.Update()

        writer = vtk.vtkBMPWriter()
        writer.SetInputData(single_im.GetOutput())
        writer.SetFileName(os.path.join(self.out_dir, 'test.bmp'))
        writer.Update()
        writer.Write()

        writer_3d = vtk.vtkXMLImageDataWriter()
        writer_3d.SetFileName(os.path.join(self.out_dir, 'test.vti'))
        writer_3d.SetInputData(slice_stack)
        writer_3d.Update()
        writer_3d.Write()


if __name__ == '__main__':
    unittest.main()
