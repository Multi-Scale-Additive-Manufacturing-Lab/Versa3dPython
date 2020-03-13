import vtk
import numpy as np
import math


def create_2d_vtk_image(val, x, y, spacing):
    img = vtk.vtkImageData()
    img.SetSpacing(spacing)
    img.SetDimensions([x, y, 1])
    img.AllocateScalars(vtk.VTK_FLOAT, 1)
    img.GetPointData().GetScalars().Fill(val)
    return img


class SlicerFactory():
    def __init__(self, ppl, printer, printhead):
        """[summary]

        Arguments:
            ppl {print_platter} -- print platter
            printer {printer_settings} -- printer settings
            printhead {printhead_settings} -- printhead settings
        """
        self._ppl = ppl
        self._printer_settings = printer_settings
        self._printhead_settings = printhead_settings

    def create_slicer(self, slicer_type):

        if('fblack' == slicer_type):
            return FullBlackSlicer(config)
        else:
            return None


def slice_poly(limit, increment, polydata):
    """slice polydata in z direction into contour

    Arguments:
        limit {list} -- min and max
        increment {float} -- thickness
        polydata {vtkpolydata} -- surface to slice

    Returns:
        list -- list of vtkpolydata contour
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
    def __init__(self, height, thickess):
        self._height = height
        self._thickness = thickess

        self._image = None

    @property
    def height(self):
        return self._height

    @property
    def thickess(self):
        return self._thickness

    @property
    def vtk_image(self):
        return self._image


class VoxelSlicer():
    def __init__(self, config):
        self._listOfActors = []

        self._plate_size = (50.0, 50.0)

        self._build_height = 100.0
        self._thickness = 0.100
        dpi = (150, 1500)
        self._slice_stack = []

        self._buid_voxel = [0]*2
        voxel_size = [0]*2

        for i in range(0, 2):
            self._buid_voxel[i] = int(
                math.ceil(self._buildBedSizeXY[i]*dpi[i]/(0.0254*1000)))
            voxel_size[i] = self._buildBedSizeXY[i]/self._buid_voxel[i]

        self._spacing = voxel_size+[self._thickness]

        self._extruder = vtk.vtkLinearExtrusionFilter()
        self._extruder.SetScaleFactor(1.)
        self._extruder.SetExtrusionTypeToNormalExtrusion()
        self._extruder.SetVector(0, 0, 1)

        self._poly2Sten = vtk.vtkPolyDataToImageStencil()
        # important for when SetVector is 0,0,1
        self._poly2Sten.SetTolerance(0)
        self._poly2Sten.SetOutputSpacing(self._spacing)
        self._poly2Sten.SetInputConnection(self._extruder.GetOutputPort())

        self._imgstenc = vtk.vtkImageStencil()
        self._imgstenc.SetStencilConnection(self._poly2Sten.GetOutputPort())
        self._imgstenc.SetBackgroundValue(255)

    def _merge_poly(self):
        """internal function that merge all the actors into a single polydata. 
        polydata is in world coord

        Returns:
            vtkPolydata -- surface
        """

        merge = vtk.vtkAppendPolyData()
        clean = vtk.vtkCleanPolyData()

        for actor in self._listOfActors:

            transform = vtk.vtkTransform()
            transform.SetMatrix(actor.GetMatrix())

            PolyData = vtk.vtkPolyData()
            PolyData.DeepCopy(actor.GetMapper().GetInput())

            LocalToWorldCoordConverter = vtk.vtkTransformPolyDataFilter()
            LocalToWorldCoordConverter.SetTransform(transform)
            LocalToWorldCoordConverter.SetInputData(PolyData)
            LocalToWorldCoordConverter.Update()

            Extent = actor.GetBounds()

            merge.AddInputData(LocalToWorldCoordConverter.GetOutput())

        merge.Update()
        clean.SetInputConnection(merge.GetOutputPort())
        clean.Update()

        return clean.GetOutput()

    def add_actor(self, actor):
        self._listOfActors.append(actor)


class FullBlackSlicer(VoxelSlicer):

    def __init__(self, config):
        super().__init__(config)

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
            if(individual_slice != None):
                self._sliceStack.append(individual_slice)

        return self._sliceStack

    def full_black_slice(self, contour, bound, black_img):
        origin = [0]*3
        contour_bounds = contour.GetBounds()
        origin[0] = bound[0]
        origin[1] = bound[2]
        origin[2] = contour_bounds[4]

        IndividualSlice = slice(origin[2], self._thickness)

        # white image origin and stencil origin must line up
        black_img.SetOrigin(origin)

        if(contour.GetNumberOfLines() > 0):
            self._extruder.SetInputData(contour)
            self._extruder.Update()

            self._poly2Sten.SetOutputOrigin(origin)
            self._poly2Sten.Update()

            self._imgstenc.SetInputData(black_img)
            self._imgstenc.Update()

            image = vtk.vtkImageData()
            image.DeepCopy(self._imgstenc.GetOutput())
            IndividualSlice.setImage(image)
            return [IndividualSlice]

        return None
