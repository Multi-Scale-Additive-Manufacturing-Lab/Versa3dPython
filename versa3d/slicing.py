import vtk
import numpy as np
import math
from vtk.util.numpy_support import vtk_to_numpy
from collections import namedtuple

Slice = namedtuple('Slice', ['height', 'thickness', 'image', 'contour'])


def convert_vtk_im_to_numpy(im):
    rows, cols, _ = im.GetDimensions()
    scalar = im.GetPointData().GetScalars()
    np_im = vtk_to_numpy(scalar)
    return np_im.reshape(rows, cols, -1)


def create_2d_vtk_image(val, x, y, spacing):
    img = vtk.vtkImageData()
    img.SetSpacing(spacing)
    img.SetDimensions([x, y, 1])
    img.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)
    img.GetPointData().GetScalars().Fill(val)
    return img


class VoxelSlicer():
    def __init__(self, polydata, print_preset, printer_setting, printhead_setting):

        self.parts = polydata

        self.print_settings = print_preset
        self.printer_attr = printer_setting
        self.printhead_attr = printhead_setting

        self._printer_dim = printer_setting.build_bed_size

        self._thickness = print_preset.layer_thickness
        self._slice_stack = []
        dpi = printhead_setting.dpi

        self._build_voxel = np.ceil(
            self._printer_dim[0:2]*dpi/(0.0254*1000)).astype(int)

        self._spacing = np.append(
            self._printer_dim[0:2]/self._build_voxel[0:2], self._thickness)

    @staticmethod
    def slice_source(heights, polydata):
        """slice polydata in z direction into contour

        Args:
            heights (ndarray): thickness
            polydata (vtkPolyData): surface to slice

        Returns:
            list: list of vtkpolydata contour
        """
        list_contour = []

        for h in heights:
            cut_plane = vtk.vtkPlane()
            cut_plane.SetOrigin(0, 0, 0)
            cut_plane.SetNormal(0, 0, 1)
            cut_plane.SetOrigin(0, 0, h)

            cutter = vtk.vtkCutter()
            cutter.SetCutFunction(cut_plane)
            cutter.SetInputData(polydata)

            stripper = vtk.vtkStripper()
            stripper.SetInputConnection(cutter.GetOutputPort())
            stripper.JoinContiguousSegmentsOn()

            stripper.Update()
            list_contour.append(stripper)

        return list_contour


class FullBlackSlicer(VoxelSlicer):

    def slice(self):
        self.parts.ComputeBounds()
        bound = self.parts.GetBounds()

        heights = np.arange(bound[4], bound[5], self._thickness)

        list_contour_src = self.slice_source(heights, self.parts)

        for contour_src in list_contour_src:
            individual_slice = self.full_black_slice(contour_src, bound)
            if(individual_slice is not None):
                self._slice_stack.append(individual_slice)

        return self._slice_stack

    def full_black_slice(self, contour_src, bound):
        origin = np.zeros(3, dtype=float)
        contour_bounds = contour_src.GetOutput().GetBounds()
        origin[0:2] = bound[0:4:2]
        origin[2] = contour_bounds[4]

        img_dim = np.zeros(3, dtype=int)

        for i in range(2):
            img_dim[i] = np.ceil(
                (bound[2*i+1]-bound[2*i])/self._spacing[i]) + 1

        img_dim[2] = 1

        black_img = create_2d_vtk_image(
            0, img_dim[0], img_dim[1], self._spacing)

        # white image origin and stencil origin must line up
        black_img.SetOrigin(origin)

        if(contour_src.GetOutput().GetNumberOfLines() > 0):

            extruder = vtk.vtkLinearExtrusionFilter()
            extruder.SetScaleFactor(1.)
            extruder.SetExtrusionTypeToNormalExtrusion()
            extruder.SetVector(0, 0, 1)
            extruder.SetInputConnection(contour_src.GetOutputPort())
            extruder.Update()

            poly2sten = vtk.vtkPolyDataToImageStencil()
            # important for when SetVector is 0,0,1
            poly2sten.SetInputConnection(extruder.GetOutputPort())
            poly2sten.SetTolerance(0)
            poly2sten.SetOutputSpacing(self._spacing)
            poly2sten.SetOutputOrigin(origin)
            poly2sten.SetOutputWholeExtent(black_img.GetExtent())
            poly2sten.Update()

            imgstenc = vtk.vtkImageStencil()
            imgstenc.SetStencilConnection(poly2sten.GetOutputPort())
            imgstenc.ReverseStencilOff()
            imgstenc.SetBackgroundValue(255)
            imgstenc.SetInputData(black_img)
            imgstenc.Update()

            image = imgstenc.GetOutput()
            return Slice(origin[2], self._thickness, image, contour_src.GetOutput())

        return None
