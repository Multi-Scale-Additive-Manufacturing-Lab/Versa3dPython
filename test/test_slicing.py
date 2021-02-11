import unittest
import os
import numpy as np
import vtk

from unittest import mock

from versa3d.slicing import VoxelSlicer


class SlicingTest(unittest.TestCase):

    def setUp(self):
        reader = vtk.vtkSTLReader()
        reader.SetFileName('./test/test_file/3DBenchySmall.stl')
        reader.Update()

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
        lt = mock.Mock()
        lt.value = 0.1

        res = mock.Mock()
        res.value = np.array([600, 600], dtype=int)

        self.printer_setting = mock.Mock()
        self.printer_setting.layer_thickness = lt

        self.printhead_setting = mock.Mock()
        self.printhead_setting.dpi = res

        self.print_param = mock.Mock()

    def test_slice_boat(self):
        self.print_param.fill_pattern.value = 0

        slicer = VoxelSlicer()
        slicer.set_settings(self.printer_setting,
                            self.printhead_setting, self.print_param)
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
    
    def test_dither_boat(self):
        self.print_param.fill_pattern.value = 1
        self.print_param.skin_offset.value = 0.1

        slicer = VoxelSlicer()
        slicer.set_settings(self.printer_setting,
                            self.printhead_setting, self.print_param)
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
        writer.SetFileName(os.path.join(self.out_dir, 'test_d.bmp'))
        writer.Update()
        writer.Write()

        writer_3d = vtk.vtkXMLImageDataWriter()
        writer_3d.SetFileName(os.path.join(self.out_dir, 'test_d.vti'))
        writer_3d.SetInputData(slice_stack)
        writer_3d.Update()
        writer_3d.Write()


if __name__ == '__main__':
    unittest.main()
