import vtk
import numpy as np
import math
from vtk.util.numpy_support import vtk_to_numpy
from collections import namedtuple

Slice = namedtuple('Slice', ['height', 'thickness', 'image'])


def convert_vtk_im_to_numpy(im):
    rows, cols, _ = im.GetDimensions()
    scalar = im.GetPointData().GetScalars()
    np_im = vtk_to_numpy(scalar)
    return np_im.reshape(rows, cols, -1)


def create_2d_vtk_image(val, x, y, spacing):
    img = vtk.vtkImageData()
    img.SetSpacing(spacing)
    img.SetDimensions([x, y, 1])
    img.AllocateScalars(vtk.VTK_FLOAT, 1)
    img.GetPointData().GetScalars().Fill(val)
    return img


def create_slicer(self, slicer_type, parts, printer, printhead, print_settings):
    if('fblack' == slicer_type):
        return FullBlackSlicer(parts, print_settings, printer, printhead)
    else:
        return None


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

        self._spacing = np.append(self._printer_dim[0:2]/self._build_voxel[0:2], self._thickness)

        self._extruder = vtk.vtkLinearExtrusionFilter()
        self._extruder.SetScaleFactor(1.)
        self._extruder.SetExtrusionTypeToNormalExtrusion()
        self._extruder.SetVector(0, 0, 1)

        self._poly2sten = vtk.vtkPolyDataToImageStencil()
        # important for when SetVector is 0,0,1
        self._poly2sten.SetTolerance(0)
        self._poly2sten.SetOutputSpacing(self._spacing)
        self._poly2sten.SetInputConnection(self._extruder.GetOutputPort())

        self._imgstenc = vtk.vtkImageStencil()
        self._imgstenc.SetStencilConnection(self._poly2sten.GetOutputPort())
        self._imgstenc.SetBackgroundValue(255)

    @staticmethod
    def slice_poly(heights, polydata):
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
            contour = stripper.GetOutput()
            list_contour.append(contour)

        return list_contour


class FullBlackSlicer(VoxelSlicer):

    def slice(self):

        self.parts.ComputeBounds()
        bound = self.parts.GetBounds()

        img_dim = [int(math.ceil((bound[2*i+1]-bound[2*i]) /
                                 self._spacing[i]))+1 for i in range(2)]

        black_img = create_2d_vtk_image(
            0, img_dim[0], img_dim[1], self._spacing)
        heights = np.arange(bound[4], bound[5], self._thickness)
        list_contour = self.slice_poly(heights, self.parts)

        for contour in list_contour:
            individual_slice = self.full_black_slice(contour, bound, black_img)
            if(individual_slice is not None):
                self._slice_stack.append(individual_slice)

        return self._slice_stack

    def full_black_slice(self, contour, bound, black_img):
        origin = [0]*3
        contour_bounds = contour.GetBounds()
        origin[0] = bound[0]
        origin[1] = bound[2]
        origin[2] = contour_bounds[4]

        # white image origin and stencil origin must line up
        black_img.SetOrigin(origin)

        if(contour.GetNumberOfLines() > 0):
            self._extruder.SetInputData(contour)
            self._extruder.Update()

            self._poly2sten.SetOutputOrigin(origin)
            self._poly2sten.Update()

            self._imgstenc.SetInputData(black_img)
            self._imgstenc.Update()

            image = convert_vtk_im_to_numpy(self._imgstenc.GetOutput())
            return Slice(origin[2], self._thickness, image)

        return None
