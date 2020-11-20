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
        input_src = vtk.vtkPolyData.GetData(inInfo[0])
        bounds = np.array(input_src.GetBounds())
        spacing = self.compute_spacing(self._layer_thickness, self._resolution)
        img_dim = self.compute_dim(bounds, spacing)
        origin = bounds[0::2]

        background_img = vtk.vtkImageData()
        background_img.SetSpacing(spacing)
        background_img.SetDimensions(img_dim)
        background_img.SetOrigin(origin)
        background_img.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)
        background_img.GetPointData().GetScalars().Fill(0)

        poly_sten = vtk.vtkPolyDataToImageStencil()
        poly_sten.SetInputData(input_src)
        poly_sten.SetOutputOrigin(origin)
        poly_sten.SetOutputSpacing(spacing)
        poly_sten.SetOutputWholeExtent(background_img.GetExtent())
        poly_sten.Update()

        stencil = vtk.vtkImageStencil()
        stencil.SetInputData(background_img)
        stencil.SetStencilConnection(poly_sten.GetOutputPort())
        stencil.SetBackgroundValue(255)
        stencil.ReverseStencilOff()
        stencil.Update()

        output = vtk.vtkImageData.GetData(outInfo)
        output.ShallowCopy(stencil.GetOutput())

        return 1