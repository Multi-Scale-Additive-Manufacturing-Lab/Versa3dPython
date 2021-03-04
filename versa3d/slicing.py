import numpy as np
from vtkmodules.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtkmodules.util.numpy_support import vtk_to_numpy, numpy_to_vtk
from vtkmodules.util.vtkConstants import VTK_DOUBLE, VTK_UNSIGNED_CHAR
from vtkmodules.vtkCommonDataModel import vtkPolyData, vtkImageData
from vtkmodules.vtkCommonCore import vtkInformation
from vtkmodules.vtkCommonExecutionModel import vtkStreamingDemandDrivenPipeline
from vtkmodules.vtkImagingStencil import vtkPolyDataToImageStencil, vtkImageStencil
from vtkmodules.vtkImagingGeneral import vtkImageEuclideanDistance
from vtkmodules.vtkImagingCore import vtkImageThreshold, vtkImageShiftScale, vtkImageMask, vtkExtractVOI

from abc import ABC, abstractmethod

from versa3d.settings import PrintSetting, PixelPrinthead, GenericPrintParameter
from enum import Enum


class DitheringEnum(Enum):
    FloydSteinberg = [
        [1, 0, 7.0 / 16.0],
        [-1, 1, 3.0 / 16.0],
        [0, 1, 5.0 / 16.0],
        [1, 1, 1.0 / 16.0]]

    Atkinson = [
        [1, 0, 7.0 / 48.0],
        [2, 0, 5.0 / 48.0],
        [-2, 1, 3.0 / 48.0],
        [-1, 1, 5.0 / 48.0],
        [0, 1, 7.0 / 48.0],
        [1, 1, 5.0 / 48.0],
        [2, 1, 3.0 / 48.0],
        [-2, 2, 1.0 / 48.0],
        [-1, 2, 3.0 / 48.0],
        [0, 2, 5.0 / 48.0],
        [0, 2, 5.0 / 48.0],
        [1, 2, 3.0 / 48.0],
        [2, 2, 1.0 / 48.0]
    ]


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
    def slice_object(self, input_src: vtkPolyData):
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

    def update_info(self, input_src: vtkInformation, outInfo: vtkInformation) -> None:
        spacing = self.compute_spacing(self._layer_thickness, self._resolution)
        bounds = np.array(input_src.GetBounds())
        img_dim = self.compute_dim(bounds, spacing)
        outInfo.Set(vtkStreamingDemandDrivenPipeline.WHOLE_EXTENT(),
                    (0, img_dim[0]-1, 0, img_dim[1]-1, 0, img_dim[2]-1), 6)

    def slice_object(self, input_src: vtkPolyData) -> vtkImageData:
        bounds = np.array(input_src.GetBounds())
        spacing = self.compute_spacing(self._layer_thickness, self._resolution)
        img_dim = self.compute_dim(bounds, spacing)
        origin = bounds[0::2]

        background_img = vtkImageData()
        background_img.SetSpacing(spacing)
        background_img.SetDimensions(img_dim)
        background_img.SetOrigin(origin)
        background_img.AllocateScalars(VTK_UNSIGNED_CHAR, 1)
        background_img.GetPointData().GetScalars().Fill(0)

        poly_sten = vtkPolyDataToImageStencil()
        poly_sten.SetInputData(input_src)
        poly_sten.SetOutputOrigin(origin)
        poly_sten.SetOutputSpacing(spacing)
        poly_sten.SetOutputWholeExtent(background_img.GetExtent())
        poly_sten.Update()

        stencil = vtkImageStencil()
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

        if setting.infill.value != self._infill:
            self._infill = setting.infill.value
            modified_flag = True

        return modified_flag

    def update_printer(self, setting: PrintSetting) -> bool:
        return False

    def update_info(self, input_src: vtkInformation, outInfo: vtkInformation) -> None:
        spacing = self.compute_spacing(self._layer_thickness, self._resolution)
        bounds = np.array(input_src.GetBounds())
        img_dim = self.compute_dim(bounds, spacing)
        outInfo.Set(vtkStreamingDemandDrivenPipeline.WHOLE_EXTENT(),
                    (0, img_dim[0]-1, 0, img_dim[1]-1, 0, img_dim[2]-1), 6)

    def slice_object(self, input_src: vtkPolyData) -> vtkImageData:
        bounds = np.array(input_src.GetBounds())
        spacing = self.compute_spacing(self._layer_thickness, self._resolution)
        img_dim = self.compute_dim(bounds, spacing)
        origin = bounds[0::2]

        foreground_img = vtkImageData()
        foreground_img.SetSpacing(spacing)
        foreground_img.SetDimensions(img_dim)
        foreground_img.SetOrigin(origin)
        foreground_img.AllocateScalars(VTK_DOUBLE, 1)
        foreground_img.GetPointData().GetScalars().Fill(1.0)

        output_im = vtkImageData()
        output_im.DeepCopy(foreground_img)
        output_im.AllocateScalars(VTK_UNSIGNED_CHAR, 1)

        poly_sten = vtkPolyDataToImageStencil()
        poly_sten.SetInputData(input_src)
        poly_sten.SetOutputOrigin(origin)
        poly_sten.SetOutputSpacing(spacing)
        poly_sten.SetOutputWholeExtent(foreground_img.GetExtent())
        poly_sten.Update()

        stencil = vtkImageStencil()
        stencil.SetInputData(foreground_img)
        stencil.SetStencilConnection(poly_sten.GetOutputPort())
        stencil.SetBackgroundValue(0.0)
        stencil.Update()

        dims = foreground_img.GetDimensions()

        for z_id in range(dims[2]):

            voi_extent = [0, dims[0] - 1,
                          0, dims[1] - 1,
                          z_id, z_id]

            voi = vtkExtractVOI()
            voi.SetVOI(voi_extent)
            voi.SetSampleRate([1]*3)
            voi.SetInputConnection(stencil.GetOutputPort())
            voi.Update()

            edt = vtkImageEuclideanDistance()
            edt.SetInputConnection(voi.GetOutputPort())
            edt.InitializeOn()
            edt.Update()

            pix_offset = self._skin_thickness/np.min(spacing)
            skin_img = vtkImageThreshold()
            skin_img.ThresholdByUpper(pix_offset)
            skin_img.SetOutputScalarTypeToFloat()
            skin_img.SetInValue(1.0 - self._infill)
            skin_img.SetOutValue(0.0)
            skin_img.SetInputConnection(edt.GetOutputPort())
            skin_img.Update()

            dithering = VoxDithering()
            dithering.SetInputConnection(skin_img.GetOutputPort())
            dithering.Update()

            test = dithering.GetOutputDataObject(0)

            full_im = vtkImageShiftScale()
            full_im.SetOutputScalarTypeToUnsignedChar()
            full_im.SetScale(255)
            full_im.SetInputConnection(voi.GetOutputPort())
            full_im.ClampOverflowOn()
            full_im.Update()

            mask = vtkImageMask()
            mask.SetImageInputData(dithering.GetOutputDataObject(0))
            mask.SetMaskInputData(full_im.GetOutput())
            mask.SetMaskedOutputValue(1)
            mask.Update()

            char_skin = vtkImageShiftScale()
            char_skin.SetOutputScalarTypeToUnsignedChar()
            char_skin.SetScale(255)
            char_skin.SetInputConnection(mask.GetOutputPort())
            char_skin.Update()

            output_im.CopyAndCastFrom(char_skin.GetOutput(), voi_extent)

        return output_im


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

    def RequestInformation(self, request: str, inInfo: vtkInformation, outInfo: vtkInformation) -> int:
        input_src = vtkPolyData.GetData(inInfo[0])
        info = outInfo.GetInformationObject(0)
        self.slicer.update_info(input_src, info)
        return 1

    def RequestData(self, request: str, inInfo: vtkInformation, outInfo: vtkInformation) -> int:
        input_src = vtkPolyData.GetData(inInfo[0])
        output = vtkImageData.GetData(outInfo)
        output.ShallowCopy(self.slicer.slice_object(input_src))
        return 1


class VoxDithering(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self,
                                        nInputPorts=1, inputType='vtkImageData',
                                        nOutputPorts=1, outputType='vtkImageData')

        self.dith_map = DitheringEnum.FloydSteinberg.value

    def closest_color(self, x: float) -> float:
        if x <= 0:
            return 0.0
        elif(x >= 1.0):
            return 1.0
        else:
            return round(x, 0)

    def RequestInformation(self, request: str, inInfo: vtkInformation, outInfo: vtkInformation) -> int:
        input_src = vtkImageData.GetData(inInfo[0])
        ext = input_src.GetExtent()
        o_info = outInfo.GetInformationObject(0)
        o_info.Set(vtkStreamingDemandDrivenPipeline.WHOLE_EXTENT(), ext, 6)
        return 1

    def RequestData(self, request: str, inInfo: vtkInformation, outInfo: vtkInformation) -> int:
        input_src = vtkImageData.GetData(inInfo[0])
        output = vtkImageData.GetData(outInfo)
        ext = input_src.GetExtent()
        output.DeepCopy(input_src)

        error_map = DitheringEnum.FloydSteinberg.value

        for i in range(ext[0], ext[1]):
            for j in range(ext[2], ext[3]):
                pix_val = output.GetScalarComponentAsDouble(i, j, ext[4], 0)
                new_val = self.closest_color(pix_val)
                output.SetScalarComponentFromDouble(i, j, ext[4], 0, new_val)
                error = pix_val - new_val
                if error != 0:
                    for m in error_map:
                        di = i + m[0]
                        dj = j + m[1]

                        if ext[0] <= di and di < ext[1] and ext[2] <= dj and dj < ext[3]:
                            old_val = output.GetScalarComponentAsDouble(
                                di, dj, ext[4], 0)
                            quantization = old_val + error*m[2]
                            output.SetScalarComponentFromDouble(
                                di, dj, ext[4], 0, quantization)

        return 1
