import vtk
import numpy as np
from src.lib.versa3dConfig import config
import math

def slicerFactory(type, config):
    
    if('black' == type):
        return FullBlackImageSlicer(config)
    elif('checker_board'==type):
        return CheckerBoardImageSlicer(config)
    else:
        return None

class VoxelSlicer():
    def __init__(self, config):
        self._listOfActors = []
        self._ListOfSlice = []

        self._thickness = config.getValue('layer_thickness')
        self._XYVoxelSize = config.getValue('xy_resolution')
    
    def voxelize(self, Actor, tol=0.5):
        PolyData = Actor.GetMapper().GetInput()
        boundingBox = PolyData.GetBounds()
        
        SampleDim = [0]*3
        ar = [self._XYVoxelSize[0],self._XYVoxelSize[1],self._thickness]
        for i in range(0,3):
            SampleDim[i] =int(math.ceil((boundingBox[2*i+1]-boundingBox[2*i])/ar[i]+1))

        voxelizer = vtk.vtkVoxelModeller()
        voxelizer.SetSampleDimensions(SampleDim)
        voxelizer.SetMaximumDistance(tol)
        voxelizer.SetModelBounds(boundingBox)
        voxelizer.SetInputData(PolyData)
        voxelizer.SetScalarTypeToUnsignedChar()
        voxelizer.SetForegroundValue(255)
        voxelizer.SetBackgroundValue(0)
        voxelizer.Update()

        voxelGeometry = voxelizer.GetOutput()

        return voxelGeometry

    def addActor(self, actor):
        self._listOfActors.append(actor)

    def exportImage(self,FolderPath,ImageNameMnemonic):
        bmpWriter = vtk.vtkBMPWriter()
        count = 0
        for IndividualSlice in self._ListOfSlice:
            bmpWriter.SetFileName(FolderPath+"/"+ImageNameMnemonic+"_"+str(count)+".bmp")

            bmpWriter.SetInputData(IndividualSlice)
            bmpWriter.Write()
            count = count+1



class FullBlackImageSlicer(VoxelSlicer):

    def __init__(self, config):
        super().__init__(config)
        
    def slice(self):
        
        for actor in self._listOfActors:
            VoxelizedShape = self.voxelize(actor)

            (xMin, xMax, yMin, yMax, zMin, zMax) = VoxelizedShape.GetExtent()
            
            for z in range(zMin,zMax):
                slicer = vtk.vtkExtractVOI()
                slicer.SetVOI(xMin,xMax,yMin,yMax,z,z)
                slicer.SetSampleRate(1,1,1)
                slicer.SetInputData(VoxelizedShape)
                slicer.Update()

                self._ListOfSlice.append(slicer.GetOutput())

        return self._ListOfSlice
            
    


class CheckerBoardImageSlicer(VoxelSlicer):

    def __init__(self, config):
        super(VoxelSlicer,self).__init__(config)
