import numpy as np
from vtkmodules.util.vtkAlgorithm import VTKPythonAlgorithmBase, vtkAlgorithm
from vtkmodules.vtkInteractionWidgets import vtkBoxWidget
from vtkmodules.vtkCommonCore import vtkInformation
from vtkmodules.vtkCommonDataModel import vtkPolyData,vtkDataObject
from vtkmodules.vtkCommonExecutionModel import vtkPolyDataAlgorithm
from vtkmodules.util.vtkConstants import VTK_OBJECT
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkRenderingCore import vtkRenderWindowInteractor, vtkActor, vtkRenderer, vtkPolyDataMapper
from vtkmodules.vtkFiltersGeneral import vtkTransformPolyDataFilter
from vtkmodules.vtkFiltersCore import vtkAppendPolyData
from vtkmodules.vtkFiltersCore import vtkMarchingCubes
from vtkmodules.util.misc import calldata_type
from vtkmodules.util import keys
from vtkmodules.vtkCommonTransforms import vtkTransform
from PyQt5.QtCore import QObject, QUuid, pyqtSlot, pyqtSignal

from typing import Callable
from time import time

from versa3d.slicing import VoxelSlicer
from versa3d.settings import PrintSetting, PixelPrinthead, GenericPrintParameter

ID_KEY = keys.MakeKey(keys.StringKey, 'id', "vtkActor")

class PrintObject():
    def __init__(self, poly_src : vtkPolyDataAlgorithm) -> None:
        self._poly_src = poly_src
        self.id = QUuid.createUuid().toString()
        self.actor = vtkActor()

        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(poly_src.GetOutputPort())
        self.actor.SetMapper(mapper)

        info = vtkInformation()
        info.Set(ID_KEY, self.id)
        self.actor.GetProperty().SetInformation(info)

        transform = vtkTransform()
        transform.SetMatrix(self.actor.GetMatrix())

        self._coord_converter = vtkTransformPolyDataFilter()
        self._coord_converter.SetTransform(transform)
        self._coord_converter.AddInputData(poly_src.GetOutput())
        self._coord_converter.Update()

        self._voxelizer = VoxelSlicer()
        self._voxelizer.SetInputConnection(self._coord_converter.GetOutputPort())

        self.results = vtkActor()

    def slice_obj(self, printer: PrintSetting,
                     printhead: PixelPrinthead,
                     print_param: GenericPrintParameter) -> None:

        transform = vtkTransform()
        transform.SetMatrix(self.actor.GetMatrix())
        self._coord_converter.SetTransform(transform)

        self._voxelizer.set_settings(printer, printhead, print_param)
        self._voxelizer.Update()

        surf = vtkMarchingCubes()
        surf.SetValue(0, 255)
        surf.AddInputData(self._voxelizer.GetOutputDataObject(0))
        surf.Update()

        polymap = vtkPolyDataMapper()
        polymap.SetInputData(surf.GetOutput())
        
        actor = vtkActor()
        actor.SetMapper(polymap)
        self.results.ShallowCopy(actor)