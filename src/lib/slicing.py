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

        xDim = int(self._buildBedSizeXY[0]/self._XYVoxelSize[0])
        yDim = int(self._buildBedSizeXY[1]/self._XYVoxelSize[1])
        zDim = int(self._buildHeight/self._thickness)

        self._BuildVolumeVox = vtk.vtkImageData()
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
        (xDim,yDim,zDim) = self._BuildVolumeVox.GetDimensions()

        for z in range(0,zDim):
            bmpWriter.SetFileName(FolderPath+"/"+ImageNameMnemonic+"_"+str(z)+".bmp")

            slicer = vtk.vtkExtractVOI()
            slicer.SetVOI(0,xDim-1,0,yDim-1,z,z)
            slicer.SetSampleRate(1,1,1)
            slicer.SetInputData(self._BuildVolumeVox)
            slicer.Update()

            bmpWriter.SetInputData(slicer.GetOutput())
            bmpWriter.Write()
        
    def convertCartesionToVoxelCoord(self,cartCoord):

        xDim = int(self._buildBedSizeXY[0]/self._XYVoxelSize[0])
        yDim = int(self._buildBedSizeXY[1]/self._XYVoxelSize[1])
        zDim = int(self._buildHeight/self._thickness)

        VoxPosition = [int(cartCoord[0]/self._buildBedSizeXY[0]*xDim),
                                 int(cartCoord[1]/self._buildBedSizeXY[1]*yDim),
                                 int(cartCoord[2]/self._buildHeight*zDim)]

        return VoxPosition


class FullBlackImageSlicer(VoxelSlicer):

    def __init__(self, config):
        super().__init__(config)
        
    def slice(self):
        listOfVoxShape = []
        listOftargetExtent = []

        (xDim,yDim,zDim) = self._BuildVolumeVox.GetDimensions()

        for actor in self._listOfActors:
            VoxelizedShape = self.voxelize(actor)
            Position = actor.GetPosition()
            extent = VoxelizedShape.GetExtent()
            VoxTargetPosition = self.convertCartesionToVoxelCoord(Position)
            
            targetExtent = []
            for i in range(0,3):
                 Min=extent[2*i]
                 Max=extent[2*i+1]
                 center = (Max-Min)/2
                 indexOffset = int(VoxTargetPosition[i]-center)
                 targetExtent.append(Min+indexOffset)
                 targetExtent.append(Max+indexOffset)

            listOfVoxShape.append(VoxelizedShape)
            listOftargetExtent.append(targetExtent)

        zMax = 0
        for eachExtent in listOftargetExtent:
            curz = eachExtent[5]
            if(zMax < curz):
                zMax = curz
                      
        for i in range(0,len(listOfVoxShape)):
            VoxShape = listOfVoxShape[i]
            targetExtent = listOftargetExtent[i]
            
            self.spliceVtkImage(self._BuildVolumeVox,VoxShape,targetExtent)

        self._BuildVolumeVox.Crop([0,xDim-1,0,yDim-1,0,zMax])
        return self._BuildVolumeVox
            
    


class CheckerBoardImageSlicer(VoxelSlicer):

    def __init__(self, config):
        super(VoxelSlicer,self).__init__(config)
