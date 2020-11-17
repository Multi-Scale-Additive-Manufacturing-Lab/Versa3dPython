import vtk
import numpy as np
import math
from vtk.util.numpy_support import vtk_to_numpy
from collections import namedtuple
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase


class VoxelSlicer(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self,
            nInputPorts=1, inputType = 'vtkPolyData', 
            nOutputPorts=1, outputType='vtkImageData')

        self._resolution = None 
        self._layer_thickness = None
    
    @property
    def resolution(self):
        return self._resolution
    
    @resolution.setter
    def resolution(self, val):
        if np.any(val != self._resolution):
            self.Modified()
            self._resolution = val
    
    @property
    def layer_thickness(self):
        return self._layer_thickness
    
    @layer_thickness.setter
    def layer_thickness(self, val):
        if np.min(val) != np.min(self._layer_thickness):
            self.Modified()
            self._layer_thickness = val
    
    @staticmethod
    def compute_spacing(layer_thickness, resolution):
        spacing = np.zeros(3, dtype=float)
        spacing[0:2] = 25.4/resolution
        spacing[2] = np.min(layer_thickness)
        return spacing
    
    @staticmethod
    def compute_dim(bounds, spacing):
        return np.ceil(( bounds[1::2] - bounds[0::2] ) / spacing).astype(int)
    
    def RequestInformation(self, request, inInfo, outInfo):
        spacing = self.compute_spacing(self._layer_thickness, self._resolution)

        input_src = vtk.vtkPolyData.GetData(inInfo[0])

        bounds = np.array(input_src.GetBounds())
        img_dim = self.compute_dim(bounds, spacing)

        info = outInfo.GetInformationObject(0)
        info.Set(vtk.vtkStreamingDemandDrivenPipeline.WHOLE_EXTENT(),
            (0, img_dim[0]-1, 0, img_dim[1]-1, 0, img_dim[2]-1), 6)
        return 1

    def RequestData(self, request, inInfo, outInfo):
        voxelizer = vtk.vtkImplicitModeller()
        voxelizer.SetMaximumDistance(0.1)
        voxelizer.SetAdjustDistance(0.1)
        voxelizer.SetProcessModeToPerVoxel()
        voxelizer.AdjustBoundsOn()
        voxelizer.SetOutputScalarTypeToUnsignedChar()

        spacing = self.compute_spacing(self._layer_thickness, self._resolution)

        input_src = vtk.vtkPolyData.GetData(inInfo[0])

        bounds = np.array(input_src.GetBounds())
        img_dim = self.compute_dim(bounds, spacing)

        voxelizer.SetSampleDimensions(img_dim)
        voxelizer.SetModelBounds(bounds)
        voxelizer.SetInputData(input_src)
        voxelizer.Update()

        output = vtk.vtkImageData.GetData(outInfo)
        output.ShallowCopy(voxelizer.GetOutput())

        return 1