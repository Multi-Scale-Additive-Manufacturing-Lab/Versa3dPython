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

        self._buildBedVolPixel = [0]*2
        self._XYVoxelSize = [0]*2

        for i in range(0,2):
            self._buildBedVolPixel[i] = int(math.ceil(self._buildBedSizeXY[i]*dpi[i]/(0.0254*1000)))
            self._XYVoxelSize[i] = self._buildBedSizeXY[i]/self._buildBedVolPixel[i]
        

    def addActor(self, actor):
        self._listOfActors.append(actor)
    
    def getBuildVolume(self):
        return self._sliceStack
    def getXYDim(self):
        return self._buildBedVolPixel
    def getSlice(self,index):
        return self._sliceStack[i]

class FullBlackImageSlicer(VoxelSlicer):

    def __init__(self, config):
        super().__init__(config)
        self._spacing = self._XYVoxelSize+[self._thickness]
        self._Dim = self._buildBedVolPixel[0:2]+[1]

        self._extruder = vtk.vtkLinearExtrusionFilter()
        self._extruder.SetScaleFactor(1.)
        self._extruder.SetExtrusionTypeToNormalExtrusion()
        self._extruder.SetVector(0, 0, 1)

        self._poly2Sten = vtk.vtkPolyDataToImageStencil()
        self._poly2Sten.SetTolerance(0) #important for when SetVector is 0,0,1
        self._poly2Sten.SetOutputSpacing(self._spacing)
        self._poly2Sten.SetInputConnection(self._extruder.GetOutputPort())
        
        self._imgstenc = vtk.vtkImageStencil()
        self._imgstenc.SetStencilConnection(self._poly2Sten.GetOutputPort())
        self._imgstenc.ReverseStencilOn()
        self._imgstenc.SetBackgroundValue(0)
        
    def slice(self):
        listOfTransformationMatrix = []

        min = self._buildBedSizeXY[0:2]+[self._buildHeight]
        max = [0]*3

        for actor in self._listOfActors:               
            forward = actor.GetMatrix()
            backward = vtk.vtkMatrix4x4()
            backward.DeepCopy(forward)
            backward.Invert()

            listOfTransformationMatrix.append((forward,backward))

            PolyData = actor.GetMapper().GetInput()
            Extent = actor.GetBounds()

            for i in range(0,3):
                if(min[i] >= Extent[2*i] ):
                    min[i] = Extent[2*i]
                
                if(max[i]<= Extent[2*i+1]):
                    max[i] = Extent[2*i+1]

        for height in np.arange(min[2],max[2]+self._thickness,self._thickness):

            IndividualSlice = slice(height,self._thickness)

            merge = vtk.vtkAppendPolyData()
            clean = vtk.vtkCleanPolyData()
            
            #homogeneous world Coord
            CutPlaneOriginWorldCoord = [0,0,height,1]
            CutPlaneNormalWorldCoord = [0,0,1,1]
            
            listOfContour = []

            for i in range(0,len(self._listOfActors)):
                actor = self._listOfActors[i]

                backward = listOfTransformationMatrix[i][1]

                originLocalCoord = backward.MultiplyPoint(CutPlaneOriginWorldCoord)
                normalLocalCoord = backward.MultiplyPoint(CutPlaneNormalWorldCoord)
                
                cutPlane = vtk.vtkPlane()
                cutPlane.SetNormal(originLocalCoord[0:3])
                cutPlane.SetOrigin(normalLocalCoord[0:3])

                PolyData = actor.GetMapper().GetInput()
                
                cutter = vtk.vtkCutter()
                cutter.SetCutFunction(cutPlane)
                cutter.SetInputData(PolyData)

                stripper = vtk.vtkStripper()
                stripper.SetInputConnection(cutter.GetOutputPort())
            
                stripper.Update()

                transform = vtk.vtkTransform()
                transform.SetMatrix(listOfTransformationMatrix[i][0])

                Filter = vtk.vtkTransformPolyDataFilter()
                Filter.SetTransform(transform)
                Filter.SetInputData(stripper.GetOutput())
                Filter.Update()

                listOfContour.append(Filter.GetOutput())
            
            merge = vtk.vtkAppendPolyData()
            clean = vtk.vtkCleanPolyData()

            for contour in listOfContour:
                merge.AddInputData(contour)
            
            merge.Update()
            clean.SetInputConnection(merge.GetOutputPort())
            clean.Update()

            mergedPoly = clean.GetOutput()
            
            imgDim = [1]*3
            for j in range(0,2):
                imgDim[j] = math.ceil((max[j]-min[j])/self._spacing[j])

            whiteImage = vtk.vtkImageData()
            whiteImage.SetSpacing(self._spacing)
            whiteImage.SetDimensions(imgDim)
            whiteImage.AllocateScalars(vtk.VTK_UNSIGNED_CHAR,1)
            whiteImage.GetPointData().GetScalars().Fill(255) 
            self._imgstenc.SetInputData(whiteImage)

            if(mergedPoly.GetNumberOfLines() > 0):
                self._extruder.SetInputData(mergedPoly)
                self._extruder.Update()
                self._poly2Sten.Update()

                self._imgstenc.Update()
                image = vtk.vtkImageData()
                image.ShallowCopy(self._imgstenc.GetOutput())
                image.SetOrigin(min)
                IndividualSlice.setImage(image)
                self._sliceStack.append(IndividualSlice)

        return self._sliceStack

class CheckerBoardImageSlicer(VoxelSlicer):

    def __init__(self, config):
        super(VoxelSlicer,self).__init__(config)
