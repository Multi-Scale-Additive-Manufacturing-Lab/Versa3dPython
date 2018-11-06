import vtk
import numpy as np
from src.lib.versa3dConfig import config
import src.lib.polyskel as sk
import math

from test.debugHelper import visualizer


def slicerFactory(config):

    if(config != None):
        type = config.getPrintSetting('fill')

        if('fblack' == type):
            return FullBlackImageSlicer(config)
        elif('checker_board' == type):
            return CheckerBoardImageSlicer(config)
        else:
            return None


def slicePoly(limit, increment, polydata):
    """slice polydata in z direction into contour

    Arguments:
        limit {list} -- min and max
        increment {float} -- thickness
        polydata {vtkpolydata} -- surface to slice

    Returns:
        list -- list of vtkpolydata contour
    """

    listOfContour = []

    for height in np.arange(limit[0], limit[1]+increment, increment):
        cutPlane = vtk.vtkPlane()
        cutPlane.SetOrigin(0, 0, 0)
        cutPlane.SetNormal(0, 0, 1)
        cutPlane.SetOrigin(0, 0, height)

        cutter = vtk.vtkCutter()
        cutter.SetCutFunction(cutPlane)
        cutter.SetInputData(polydata)

        stripper = vtk.vtkStripper()
        stripper.SetInputConnection(cutter.GetOutputPort())
        stripper.JoinContiguousSegmentsOn()

        stripper.Update()
        contour = stripper.GetOutput()
        listOfContour.append(contour)

    return listOfContour


class slice():
    def __init__(self, height, thickess):
        self._height = height
        self._thickness = thickess

        self._image = None

    def getThickness(self):
        return self._thickness

    def getHeight(self):
        return self._height

    def getImage(self):
        return self._image

    def setImage(self, image):
        self._image = image


class VoxelSlicer():
    def __init__(self, config):
        self._listOfActors = []

        self._buildBedSizeXY = config.getMachineSetting('printbedsize')

        self._buildHeight = config.getMachineSetting('buildheight')
        self._thickness = config.getPrintSetting('layer_thickness')
        dpi = config.getPrintHeadSetting('dpi')
        self._sliceStack = []

        self._buildBedVolPixel = [0]*2
        XYVoxelSize = [0]*2

        for i in range(0, 2):
            self._buildBedVolPixel[i] = int(
                math.ceil(self._buildBedSizeXY[i]*dpi[i]/(0.0254*1000)))
            XYVoxelSize[i] = self._buildBedSizeXY[i]/self._buildBedVolPixel[i]

        self._spacing = XYVoxelSize+[self._thickness]

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
        self._imgstenc.ReverseStencilOn()
        self._imgstenc.SetBackgroundValue(0)

    def _mergePoly(self):
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

    def addActor(self, actor):
        self._listOfActors.append(actor)

    def getBuildVolume(self):
        return self._sliceStack

    def getXYDim(self):
        return self._buildBedVolPixel

    def getSlice(self, index):
        return self._sliceStack[index]


class FullBlackImageSlicer(VoxelSlicer):

    def __init__(self, config):
        super().__init__(config)

    def slice(self):

        mergedPoly = self._mergePoly()

        mergedPoly.ComputeBounds()
        bound = mergedPoly.GetBounds()

        imgDim = [1]*3
        for i in range(0, 2):
            imgDim[i] = int(
                math.ceil((bound[2*i+1]-bound[2*i])/self._spacing[i]))+1

        whiteImage = vtk.vtkImageData()
        whiteImage.SetSpacing(self._spacing)
        whiteImage.SetDimensions(imgDim)
        whiteImage.AllocateScalars(vtk.VTK_FLOAT, 1)
        whiteImage.GetPointData().GetScalars().Fill(255)
        self._imgstenc.SetInputData(whiteImage)

        listOfContour = slicePoly(bound[4:6], self._thickness, mergedPoly)

        for contour in listOfContour:

            origin = [0]*3
            ContourBounds = contour.GetBounds()
            origin[0] = bound[0]
            origin[1] = bound[2]
            origin[2] = ContourBounds[4]

            IndividualSlice = slice(origin[2], self._thickness)

            # white image origin and stencil origin must line up
            whiteImage.SetOrigin(origin)

            if(contour.GetNumberOfLines() > 0):
                self._extruder.SetInputData(contour)
                self._extruder.Update()

                self._poly2Sten.SetOutputOrigin(origin)
                self._poly2Sten.Update()

                self._imgstenc.Update()
                image = vtk.vtkImageData()
                image.ShallowCopy(self._imgstenc.GetOutput())
                IndividualSlice.setImage(image)
                self._sliceStack.append(IndividualSlice)

        return self._sliceStack


class CheckerBoardImageSlicer(VoxelSlicer):

    def __init__(self, config):
        super().__init__(config)

        self.shell_thickness = 0.1
        self.fill_density = 0.50

    def slice(self):

        mergedPoly = self._mergePoly()

        mergedPoly.ComputeBounds()
        bound = mergedPoly.GetBounds()

        imgDim = [1]*3
        for i in range(0, 2):
            imgDim[i] = int(
                math.ceil((bound[2*i+1]-bound[2*i])/self._spacing[i]))+1

        whiteImage = vtk.vtkImageData()
        whiteImage.SetSpacing(self._spacing)
        whiteImage.SetDimensions(imgDim)
        whiteImage.AllocateScalars(vtk.VTK_FLOAT, 1)
        whiteImage.GetPointData().GetScalars().Fill(255)
        self._imgstenc.SetInputData(whiteImage)

        grey_image = vtk.vtkImageData()
        grey_image.SetSpacing(self._spacing)
        grey_image.SetDimensions(imgDim)
        grey_image.AllocateScalars(vtk.VTK_FLOAT, 1)
        grey_image.GetPointData().GetScalars().Fill(255*self.fill_density)

        listOfContour = slicePoly(bound[4:6], self._thickness, mergedPoly)

        for contour in listOfContour:

            origin = [0]*3
            ContourBounds = contour.GetBounds()
            origin[0] = bound[0]
            origin[1] = bound[2]
            origin[2] = ContourBounds[4]

            IndividualSlice = slice(origin[2], self._thickness)

            # white image origin and stencil origin must line up
            whiteImage.SetOrigin(origin)

            if(contour.GetNumberOfLines() > 0):
                skeletonizer = sk.VtkSkeletonize()
                skeletonizer.set_shell_thickness(self.shell_thickness)
                skeletonizer.AddInputDataObject(0, contour)
                skeletonizer.Update()

                merge = vtk.vtkAppendPolyData()
                merge.AddInputData(contour)
                merge.AddInputData(skeletonizer.GetOutputDataObject(0))
                merge.Update()

                self._extruder.SetInputData(merge.GetOutput())
                self._extruder.Update()

                self._poly2Sten.SetOutputOrigin(origin)
                self._poly2Sten.Update()

                self._imgstenc.Update()
                image = vtk.vtkImageData()

                int_extruder = vtk.vtkLinearExtrusionFilter()
                int_extruder.SetScaleFactor(1.)
                int_extruder.SetExtrusionTypeToNormalExtrusion()
                int_extruder.SetVector(0, 0, 1)
                int_extruder.SetInputData(skeletonizer.GetOutputDataObject(0))
                int_extruder.Update()

                int_poly_sten = vtk.vtkPolyDataToImageStencil()
                # important for when SetVector is 0,0,1
                int_poly_sten.SetTolerance(0)
                int_poly_sten.SetOutputSpacing(self._spacing)
                int_poly_sten.SetInputConnection(int_extruder.GetOutputPort())
                int_poly_sten.SetOutputOrigin(origin)
                int_poly_sten.Update()

                int_img_stenc = vtk.vtkImageStencil()
                int_img_stenc.SetStencilConnection(
                    int_poly_sten.GetOutputPort())
                int_img_stenc.SetInputData(grey_image)
                int_img_stenc.SetBackgroundInputData(
                    self._imgstenc.GetOutput())
                int_img_stenc.Update()

                image.ShallowCopy(int_img_stenc.GetOutput())
                IndividualSlice.setImage(image)
                self._sliceStack.append(IndividualSlice)

        return self._sliceStack
