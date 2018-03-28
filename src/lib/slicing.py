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
        dpi = config.getValue('dpi')
        self.listOfVoxShape = []
        self._buildBedVolPixel = [0]*3
        self._XYVoxelSize = [0]*2
        for i in range(0,2):
            self._buildBedVolPixel[i] = int(math.ceil(self._buildBedSizeXY[i]*dpi[i]/(0.0254*1000)))
            self._XYVoxelSize[i] = self._buildBedSizeXY[i]/self._buildBedVolPixel[i]
        
        self._buildBedVolPixel[2] = math.ceil(self._buildHeight/self._thickness)

        self._BuildVolumeVox = vtk.vtkImageData()
        self._BuildVolumeVox.SetSpacing(self._XYVoxelSize[0],self._XYVoxelSize[1],self._thickness)
        self._BuildVolumeVox.SetDimensions(self._buildBedVolPixel)
        self._BuildVolumeVox.AllocateScalars(vtk.VTK_UNSIGNED_CHAR,1)
        self._BuildVolumeVox.GetPointData().GetScalars().Fill(255)

        self._ceiling = 0
    
    
    def voxelize(self, Actor, tol=0.05):
        PolyData = Actor.GetMapper().GetInput()
        boundingBox = PolyData.GetBounds()
        Extent = Actor.GetBounds()

        RealDim = [Extent[1]-Extent[0],Extent[3]-Extent[2],Extent[5]-Extent[4]]
        sampleDim = [x+1 for x in self.convertCartesionToVoxelCoord(RealDim)]

        voxelizer = vtk.vtkImplicitModeller()
        voxelizer.SetSampleDimensions(sampleDim)
        voxelizer.SetMaximumDistance(tol)
        voxelizer.SetInputData(PolyData)
        voxelizer.SetModelBounds(boundingBox)
        voxelizer.SetProcessModeToPerVoxel()
        voxelizer.SetOutputScalarTypeToUnsignedChar()
        voxelizer.SetNumberOfThreads(8)
        voxelizer.Update()

        voxelGeometry = voxelizer.GetOutput()
        voxelGeometry.SetOrigin(Extent[0],Extent[2],Extent[4])        

        return voxelGeometry

    def addActor(self, actor):
        self._listOfActors.append(actor)

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

            if (z <= self._ceiling ):
                bmpWriter.SetInputData(slicer.GetOutput())
                bmpWriter.Write()
            
              
    def convertCartesionToVoxelCoord(self,cartCoord):

        VoxPosition = [int(cartCoord[0]/self._XYVoxelSize[0]),
                    int(cartCoord[1]/self._XYVoxelSize[1]),
                    int(cartCoord[2]/self._thickness)]

        return VoxPosition

    def spliceVtkImage(self,InputImage):
        (x_dim, y_dim,z_dim) = InputImage.GetDimensions()
        origin = InputImage.GetOrigin()
        originVox = self.convertCartesionToVoxelCoord(origin)

        xExtent = range(originVox[0],originVox[0]+x_dim)
        yExtent = range(originVox[1],originVox[1]+y_dim)
        zExtent = range(originVox[2],originVox[2]+z_dim)

        for x in range(0,x_dim):
            for y in range(0,y_dim):
                for z in range(0,z_dim):
                    val = InputImage.GetScalarComponentAsFloat(x,y,z,0)
                    self._BuildVolumeVox.SetScalarComponentFromFloat(xExtent[x],yExtent[y],zExtent[z],0, val)
    
    def getBuildVolume(self):
        return self._BuildVolumeVox
    
    def getCeiling(self):
        return self._ceiling

class FullBlackImageSlicer(VoxelSlicer):

    def __init__(self, config):
        super().__init__(config)
        
    def slice(self):
        listOfTargetExtent = []
        maxZ = 0
        for actor in self._listOfActors:
            VoxelizedShape = self.voxelize(actor)
            (xDim,yDim,zDim) = VoxelizedShape.GetDimensions()
            self.listOfVoxShape.append(VoxelizedShape)
            self.spliceVtkImage(VoxelizedShape)

            actorMaxZ = actor.GetBounds()[5]

            if(actorMaxZ > maxZ):
                maxZ = actorMaxZ
        
        self._ceiling = math.ceil(maxZ/self._thickness)

        return self._BuildVolumeVox
            
    


class CheckerBoardImageSlicer(VoxelSlicer):

    def __init__(self, config):
        super(VoxelSlicer,self).__init__(config)
