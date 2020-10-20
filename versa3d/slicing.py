import vtk
import numpy as np
import math
from vtk.util.numpy_support import vtk_to_numpy

from versa3d.settings import PrinterSettings, PrintheadSettings, PrintSettings


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


class SlicerFactory():
    def __init__(self, ppl, printer, printhead, printsetting):
        """ Slicer Factory

        Args:
            ppl (PrintPlatter): print platter
            printer (PrinterSettings): printer settings
            printhead (PrintheadSettings): printhead settings
            printsetting (PrintSettings): print settings
        """
        self._ppl = ppl
        self._printer_settings = printer
        self._printhead_settings = printhead
        self._print_preset = printsetting

    def create_slicer(self, slicer_type):

        if('fblack' == slicer_type):
            return FullBlackSlicer(self._ppl, self._print_preset, self._printer_settings, self._printhead_settings)
        else:
            return None


def slice_poly(limit, increment, polydata):
    """slice polydata in z direction into contour

    Args:
        limit (list): min and max
        increment (float): thickness
        polydata (vtkPolyData): surface to slice

    Returns:
        list: list of vtkpolydata contour
    """

    list_contour = []

    for height in np.arange(limit[0], limit[1]+increment, increment):
        cut_plane = vtk.vtkPlane()
        cut_plane.SetOrigin(0, 0, 0)
        cut_plane.SetNormal(0, 0, 1)
        cut_plane.SetOrigin(0, 0, height)

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


class Slice():
    def __init__(self, height, thickess, img):
        self._height = height
        self._thickness = thickess

        self._image = img

    @property
    def height(self):
        return self._height

    @property
    def thickess(self):
        return self._thickness

    @property
    def image(self):
        return self._image


class VoxelSlicer():
    def __init__(self, print_platter, print_preset_name, printer_name, printhead_name):

        self._list_parts = print_platter.parts

        print_settings = PrintSettings(print_preset_name)
        printer_attr = PrinterSettings(printer_name)
        printhead_attr = PrintheadSettings(printhead_name)

        self._printer_dim = printer_attr.bds

        self._thickness = print_settings.lt
        self._slice_stack = []
        dpi = printhead_attr.dpi

        self._build_voxel = [0]*2
        voxel_size = [0]*2

        for i in range(0, 2):
            self._build_voxel[i] = int(
                math.ceil(self._printer_dim[i]*dpi[i]/(0.0254*1000)))
            voxel_size[i] = self._printer_dim[i]/self._build_voxel[i]

        self._spacing = voxel_size+[self._thickness]

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

    def _merge_poly(self):
        """internal function that merge all the actors into a single polydata. 
        polydata is in world coord

        Returns:
            vtkPolydata: surface
        """

        merge = vtk.vtkAppendPolyData()
        clean = vtk.vtkCleanPolyData()

        for part in self._list_parts:

            vtk_actor = part.actor

            transform = vtk.vtkTransform()
            transform.SetMatrix(vtk_actor.GetMatrix())

            polydata = vtk.vtkPolyData()
            polydata.DeepCopy(vtk_actor.GetMapper().GetInput())

            coord_sys_convert = vtk.vtkTransformPolyDataFilter()
            coord_sys_convert.SetTransform(transform)
            coord_sys_convert.SetInputData(polydata)
            coord_sys_convert.Update()

            merge.AddInputData(coord_sys_convert.GetOutput())

        merge.Update()
        clean.SetInputConnection(merge.GetOutputPort())
        clean.Update()

        return clean.GetOutput()


class FullBlackSlicer(VoxelSlicer):

    def slice(self):

        merged_poly = self._merge_poly()

        merged_poly.ComputeBounds()
        bound = merged_poly.GetBounds()

        img_dim = [int(math.ceil((bound[2*i+1]-bound[2*i]) /
                                 self._spacing[i]))+1 for i in range(2)]

        black_img = create_2d_vtk_image(
            0, img_dim[0], img_dim[1], self._spacing)

        list_contour = slice_poly(bound[4:6], self._thickness, merged_poly)

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
            return [slice(origin[2], self._thickness, image)]

        return None
