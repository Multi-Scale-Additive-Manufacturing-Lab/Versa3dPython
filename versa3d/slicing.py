import vtk
import numpy as np
from vtkmodules.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtkmodules.util.numpy_support import vtk_to_numpy, numpy_to_vtk
from vtkmodules.util.vtkConstants import VTK_FLOAT

from abc import ABC, abstractmethod

from versa3d.settings import PrintSetting, PixelPrinthead, GenericPrintParameter


class GenericSlicer(ABC):
    @abstractmethod
    def update_printer(self, setting: PrintSetting):
        raise NotImplementedError

    @abstractmethod
    def update_printhead(self, setting: PrintSetting):
        raise NotImplementedError

    @abstractmethod
    def update_param(self, setting: PrintSetting):
        raise NotImplementedError

    @abstractmethod
    def slice_object(self, input_src: vtk.vtkPolyData):
        pass
    
    @staticmethod
    def compute_spacing(layer_thickness: float, resolution: float) -> np.array:
        spacing = np.zeros(3, dtype=float)
        spacing[0:2] = 25.4/resolution
        spacing[2] = np.min(layer_thickness)
        return spacing
    
    @staticmethod
    def compute_dim(bounds: np.array, spacing: np.array) -> np.array:
        return np.ceil((bounds[1::2] - bounds[0::2]) / spacing).astype(int)


class FullBlackSlicer(GenericSlicer):
    def __init__(self) -> None:
        self._resolution = np.array([50, 50], dtype=int)
        self._layer_thickness = 0.1

    def update_printhead(self, setting: PixelPrinthead) -> bool:
        if np.any(setting.dpi.value != self._resolution):
            self._resolution = setting.dpi.value
            return True
        return False

    def update_param(self, setting: GenericPrintParameter) -> bool:
        if setting.layer_thickness.value != self._layer_thickness:
            self._resolution = setting.layer_thickness.value
            return True
        return False

    def update_printer(self, setting: PrintSetting) -> bool:
        return False

    def update_info(self, input_src: vtk.vtkInformation, outInfo: vtk.vtkInformation) -> None:
        spacing = self.compute_spacing(self._layer_thickness, self._resolution)
        bounds = np.array(input_src.GetBounds())
        img_dim = self.compute_dim(bounds, spacing)
        outInfo.Set(vtk.vtkStreamingDemandDrivenPipeline.WHOLE_EXTENT(),
                    (0, img_dim[0]-1, 0, img_dim[1]-1, 0, img_dim[2]-1), 6)

    def slice_object(self, input_src: vtk.vtkPolyData) -> vtk.vtkImageData:
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
        return stencil.GetOutput()

class Dithering(GenericSlicer):
    def __init__(self) -> None:
        self._resolution = np.array([50, 50], dtype=int)
        self._layer_thickness = 0.1
        self._skin_thickness = 0.1
        self._infill = 0.80
        self._dithering = 0
    
    def update_printhead(self, setting: PixelPrinthead) -> bool:
        if np.any(setting.dpi.value != self._resolution):
            self._resolution = setting.dpi.value
            return True
        return False

    def update_param(self, setting: GenericPrintParameter) -> bool:
        modified_flag = False

        if setting.layer_thickness.value != self._layer_thickness:
            self._resolution = setting.layer_thickness.value
            modified_flag = True

        if setting.skin_offset.value != self._skin_thickness:
            self._skin_thickness = setting.skin_offset.value
            modified_flag = True
        
        return modified_flag

    def update_printer(self, setting: PrintSetting) -> bool:
        return False
    
    def update_info(self, input_src: vtk.vtkInformation, outInfo: vtk.vtkInformation) -> None:
        spacing = self.compute_spacing(self._layer_thickness, self._resolution)
        bounds = np.array(input_src.GetBounds())
        img_dim = self.compute_dim(bounds, spacing)
        outInfo.Set(vtk.vtkStreamingDemandDrivenPipeline.WHOLE_EXTENT(),
                    (0, img_dim[0]-1, 0, img_dim[1]-1, 0, img_dim[2]-1), 6)
    
    def slice_object(self, input_src: vtk.vtkPolyData) -> vtk.vtkImageData:
        bounds = np.array(input_src.GetBounds())
        spacing = self.compute_spacing(self._layer_thickness, self._resolution)
        img_dim = self.compute_dim(bounds, spacing)
        origin = bounds[0::2]

        background_img = vtk.vtkImageData()
        background_img.SetSpacing(spacing)
        background_img.SetDimensions(img_dim)
        background_img.SetOrigin(origin)
        background_img.AllocateScalars(VTK_FLOAT, 1)
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
        stencil.SetBackgroundValue(1.0)
        stencil.ReverseStencilOn()
        stencil.Update()

        edt = vtk.vtkImageEuclideanDistance()
        edt.SetInputConnection(stencil.GetOutputPort())
        edt.InitializeOn()
        edt.Update()

        pix_offset = self._skin_thickness/np.min(spacing)
        skin_img = vtk.vtkImageThreshold()
        skin_img.ThresholdByUpper(pix_offset)
        skin_img.SetOutputScalarTypeToFloat()
        skin_img.SetInValue(self._infill)
        skin_img.SetOutValue(0)
        skin_img.SetInputConnection(edt.GetOutputPort())
        skin_img.Update()

        mask_im = vtk.vtkImageShiftScale()
        mask_im.SetOutputScalarTypeToUnsignedChar()
        mask_im.SetScale(255)
        mask_im.SetInputConnection(stencil.GetOutputPort())
        mask_im.Update()

        mask = vtk.vtkImageMask()
        mask.SetImageInputData(skin_img.GetOutput())
        mask.SetMaskInputData(mask_im.GetOutput())
        mask.SetNotMask(0)
        mask.SetMaskedOutputValue(1)
        mask.Update()

        char_skin = vtk.vtkImageShiftScale()
        char_skin.SetOutputScalarTypeToUnsignedChar()
        char_skin.SetScale(255)
        char_skin.SetInputConnection(mask.GetOutputPort())
        char_skin.Update()

        return char_skin.GetOutput()

class VoxelSlicer(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self,
                                        nInputPorts=1, inputType='vtkPolyData',
                                        nOutputPorts=1, outputType='vtkImageData')

        self.slicer = None

    def set_settings(self, printer: PrintSetting,
                     printhead: PixelPrinthead,
                     print_param: GenericPrintParameter) -> None:
        self.set_print_parameter(print_param)
        self.set_printer(printer)
        self.set_printhead(printhead)

    def set_printer(self, setting: PrintSetting) -> None:
        if self.slicer.update_printer(setting):
            self.Modified()

    def set_printhead(self, setting: PixelPrinthead) -> None:
        if self.slicer.update_printhead(setting):
            self.Modified()

    def set_print_parameter(self, setting: GenericPrintParameter) -> None:
        if setting.fill_pattern.value == 0:
            self.slicer = FullBlackSlicer()
        elif setting.fill_pattern.value == 1:
            self.slicer = Dithering()
        else:
            raise ValueError

        if self.slicer.update_param(setting):
            self.Modified()

    def RequestInformation(self, request: str, inInfo: vtk.vtkInformation, outInfo: vtk.vtkInformation) -> int:
        input_src = vtk.vtkPolyData.GetData(inInfo[0])
        info = outInfo.GetInformationObject(0)
        self.slicer.update_info(input_src, info)
        return 1

    def RequestData(self, request: str, inInfo: vtk.vtkInformation, outInfo: vtk.vtkInformation) -> int:
        input_src = vtk.vtkPolyData.GetData(inInfo[0])
        output = vtk.vtkImageData.GetData(outInfo)
        output.ShallowCopy(self.slicer.slice_object(input_src))
        return 1
