import vtk
import numpy as np
from src.lib.versa3dConfig import config
import math

def slicerFactory(config):

    if(config != None):
        type = config.getPrintSetting('fill')

        if('fblack' == type):
            return FullBlackImageSlicer(config)
        elif('checker_board'==type):
            return CheckerBoardImageSlicer(config)
        else:
            return None

class slice():
    def __init__(self, height,spacing, Dimensions):
        self._height = height
        self._thickness = spacing[2]

        self._image = vtk.vtkImageData()
        self._image.SetSpacing(spacing)
        self._image.SetDimensions(Dimensions)
        self._image.AllocateScalars(vtk.VTK_UNSIGNED_CHAR,1)
        self._image.GetPointData().GetScalars().Fill(255)

    def getThickness(self):
        return self._thickness
    
    def getHeight(self):
        return self._height
    
    def getImage(self):
        return self._image
    
    def setImage(self,image):
        self._image = image
 
class VoxelSlicer():
    def __init__(self, config):
        self._listOfActors = []
        
        self._buildBedSizeXY = config.getMachineSetting('printbedsize')

        self._buildHeight = config.getMachineSetting('buildheight')
        self._thickness = config.getPrintSetting('layer_thickness')
        dpi = config.getPrintHeadSetting('dpi')
        self.listOfVoxShape = []
        self._sliceStack = []

        self._buildBedVolPixel = [0]*3
        self._XYVoxelSize = [0]*2

        for i in range(0,2):
            self._buildBedVolPixel[i] = int(math.ceil(self._buildBedSizeXY[i]*dpi[i]/(0.0254*1000)))
            self._XYVoxelSize[i] = self._buildBedSizeXY[i]/self._buildBedVolPixel[i]
        
        self._buildBedVolPixel[2] = math.ceil(self._buildHeight/self._thickness)

    def addActor(self, actor):
        self._listOfActors.append(actor)
              

class FullBlackImageSlicer(VoxelSlicer):

    def __init__(self, config):
        super().__init__(config)

        self._cutter = vtk.vtkCutter()
        self._cutPlane = vtk.vtkPlane()
        self._cutPlane.SetOrigin(0,0,0)
        self._cutPlane.SetNormal(0,0,1)

        self._cutter.SetCutFunction(self._cutPlane)

        self._stripper = vtk.vtkStripper()
        self._stripper.SetInputConnection(self._cutter.GetOutputPort())
        
    def slice(self):
        listOfTargetExtent = []
        minZ = self._buildHeight
        maxZ = 0
        listOfZInterval = []

        for actor in self._listOfActors:

                PolyData = actor.GetMapper().GetInput()
                Extent = actor.GetBounds()

                self._cutter.AddInputDataObject(PolyData)
                if(minZ >= Extent[4]):
                    minZ = Extent[4]

                if(maxZ<= Extent[5]): 
                    maxZ = Extent[5]

        for height in np.arange(minZ-self._thickness,maxZ+self._thickness,self._thickness):
            spacing = self._XYVoxelSize+[self._thickness]
            Dim = self._buildBedVolPixel[0:2]+[1]

            IndividualSlice = slice(height,spacing,Dim)

            self._cutPlane.SetOrigin(0,0,height)
            self._stripper.Update()

            contour = self._stripper.GetOutput()

            ContourBounds = contour.GetBounds()
            origin = [0]*3

            origin[0] = ContourBounds[0]
            origin[1] = ContourBounds[2]
            origin[2] = ContourBounds[4]

            extruder = vtk.vtkLinearExtrusionFilter()
            extruder.SetInputData(contour)
            extruder.SetScaleFactor(1.)
            extruder.SetExtrusionTypeToNormalExtrusion()
            extruder.SetVector(0, 0, 1)
            extruder.Update()

            poly2Sten = vtk.vtkPolyDataToImageStencil()
            poly2Sten.SetTolerance(0) #important for when SetVector is 0,0,1
            poly2Sten.SetInputConnection(extruder.GetOutputPort())
            poly2Sten.SetOutputOrigin(origin)
            poly2Sten.SetOutputSpacing(spacing)
            poly2Sten.SetOutputWholeExtent(0,Dim[0]-1,0,Dim[1]-1,0,Dim[2]-1)
            poly2Sten.Update()

            imgstenc = vtk.vtkImageStencil()
            imgstenc.SetInputData(IndividualSlice.getImage())
            imgstenc.SetStencilConnection(poly2Sten.GetOutputPort())
            imgstenc.ReverseStencilOff()
            imgstenc.SetBackgroundValue(255)
            imgstenc.Update()

            IndividualSlice.setImage(imgstenc.GetOutput())
            self._sliceStack.append(IndividualSlice)

        return self._sliceStack

class CheckerBoardImageSlicer(VoxelSlicer):

    def __init__(self, config):
        super(VoxelSlicer,self).__init__(config)
