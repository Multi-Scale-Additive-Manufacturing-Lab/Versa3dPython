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

        self._buildBedSizeXY = config.getValue('printbedsize')
        self._buildHeight = config.getValue('buildheight')
        self._thickness = config.getValue('layer_thickness')
        self._XYVoxelSize = config.getValue('xy_resolution')

        self._BuildVolumeVox = vtk.vtkImageData()
        xDim = int(self._buildBedSizeXY[0]/self._XYVoxelSize[0])
        yDim = int(self._buildBedSizeXY[1]/self._XYVoxelSize[1])
        zDim = int(self._buildHeight/self._thickness)
        self._BuildVolumeVox.SetSpacing(self._XYVoxelSize[0],self._XYVoxelSize[1],self._thickness)
        self._BuildVolumeVox.SetDimensions(xDim,yDim,zDim)
        self._BuildVolumeVox.AllocateScalars(vtk.VTK_UNSIGNED_CHAR,1)
        self._BuildVolumeVox.GetPointData().GetScalars().Fill(255)
    
    def voxelize(self, Actor, tol=0.5):
        PolyData = Actor.GetMapper().GetInput()
        boundingBox = PolyData.GetBounds()
        
        SampleDim = [0]*3
        ar = [self._XYVoxelSize[0],self._XYVoxelSize[1],self._thickness]
        for i in range(0,3):
            SampleDim[i] =int(math.ceil((boundingBox[2*i+1]-boundingBox[2*i])/ar[i]+1))

        voxelizer = vtk.vtkImplicitModeller()
        voxelizer.SetSampleDimensions(SampleDim)
        voxelizer.SetMaximumDistance(tol)
        voxelizer.SetModelBounds(boundingBox)
        voxelizer.SetInputData(PolyData)
        voxelizer.AdjustBoundsOn()
        voxelizer.SetAdjustDistance(tol)
        voxelizer.SetProcessModeToPerVoxel()
        voxelizer.SetOutputScalarTypeToUnsignedChar()
        voxelizer.SetNumberOfThreads(3)
        voxelizer.Update()

        voxelGeometry = voxelizer.GetOutput()

        return voxelGeometry

    def addActor(self, actor):
        self._listOfActors.append(actor)

    def spliceVtkImage(self,TargetImage,InputImage,Extent):
        (x_dim, y_dim,z_dim) = InputImage.GetDimensions()
        xExtent = range(Extent[0],Extent[1]+1)
        yExtent = range(Extent[2],Extent[3]+1)
        zExtent = range(Extent[4],Extent[5]+1)

        for x in range(0,x_dim):
            for y in range(0,y_dim):
                for z in range(0,z_dim):
                    val = InputImage.GetScalarComponentAsFloat(x,y,z,0)
                    TargetImage.SetScalarComponentFromFloat(xExtent[x],yExtent[y],zExtent[z],0, val)

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
        listOfVoxShape = []
        listOfPosition= []
        for actor in self._listOfActors:
            VoxelizedShape = self.voxelize(actor)
            Position = actor.GetPosition()
            listOfVoxShape.append(VoxelizedShape)
            listOfPosition.append(Position)

        (xDim,yDim,zDim) = self._BuildVolumeVox.GetDimensions()
        
        for i in range(0,len(listOfVoxShape)):
            VoxShape = listOfVoxShape[i]
            ActorPosition = listOfPosition[i]
            extent = VoxShape.GetExtent()
            VoxTargetPosition = [int(ActorPosition[0]/self._buildBedSizeXY[0]*xDim),
                                 int(ActorPosition[1]/self._buildBedSizeXY[1]*yDim),
                                 int(ActorPosition[2]/self._buildHeight*zDim)]
            
            targetExtent = []
            for i in range(0,3):
                 Min=extent[2*i]
                 Max=extent[2*i+1]
                 center = (Max-Min)/2
                 indexOffset = int(VoxTargetPosition[i]-center)
                 targetExtent.append(Min+indexOffset)
                 targetExtent.append(Max+indexOffset)
            
            self.spliceVtkImage(self._BuildVolumeVox,VoxShape,targetExtent)
        
        return self._BuildVolumeVox
            
    


class CheckerBoardImageSlicer(VoxelSlicer):

    def __init__(self, config):
        super(VoxelSlicer,self).__init__(config)
