import vtk
import numpy as np
from src.lib.versa3dConfig import config
import math

from test.debugHelper import visualizer

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
    def __init__(self, height,thickess):
        self._height = height
        self._thickness = thickess

        self._image = None

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
        self._spacing = self._XYVoxelSize+[self._thickness]
        self._Dim = self._buildBedVolPixel[0:2]+[1]

        self._cutter = vtk.vtkCutter()

        self._stripper = vtk.vtkStripper()
        self._stripper.SetInputConnection(self._cutter.GetOutputPort())

        whiteImage = vtk.vtkImageData()
        whiteImage.SetSpacing(self._spacing)
        whiteImage.SetDimensions(self._Dim)
        whiteImage.AllocateScalars(vtk.VTK_UNSIGNED_CHAR,1)
        whiteImage.GetPointData().GetScalars().Fill(255)

        self._extruder = vtk.vtkLinearExtrusionFilter()
        self._extruder.SetScaleFactor(1.)
        self._extruder.SetExtrusionTypeToNormalExtrusion()
        self._extruder.SetVector(0, 0, 1)

        self._poly2Sten = vtk.vtkPolyDataToImageStencil()
        self._poly2Sten.SetTolerance(0) #important for when SetVector is 0,0,1
        self._poly2Sten.SetOutputSpacing(self._spacing)
        self._poly2Sten.SetOutputWholeExtent(0,self._Dim[0]-1,0,self._Dim[1]-1,0,self._Dim[2]-1)
        self._poly2Sten.SetInputConnection(self._extruder.GetOutputPort())
        
        self._imgstenc = vtk.vtkImageStencil()
        self._imgstenc.SetStencilConnection(self._poly2Sten.GetOutputPort())
        self._imgstenc.SetInputData(whiteImage)
        self._imgstenc.ReverseStencilOn()
        self._imgstenc.SetBackgroundValue(0)
        
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

        for height in np.arange(minZ,maxZ+self._thickness,self._thickness):
            
            IndividualSlice = slice(height,self._thickness)

            cutPlane = vtk.vtkPlane()
            cutPlane.SetOrigin(0,0,0)
            cutPlane.SetNormal(0,0,1)
            cutPlane.SetOrigin(0,0,height)

            self._cutter.SetCutFunction(cutPlane)

            self._stripper.Update()
            contour = self._stripper.GetOutput()

            #visualizer(contour)

            ContourBounds = contour.GetBounds()
            origin = [0]*3

            origin[0] = ContourBounds[0]
            origin[1] = ContourBounds[2]
            origin[2] = ContourBounds[4]

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
        super(VoxelSlicer,self).__init__(config)
