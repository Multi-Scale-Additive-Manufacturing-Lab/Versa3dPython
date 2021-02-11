import numpy as np
from vtkmodules.util.vtkAlgorithm import VTKPythonAlgorithmBase, vtkAlgorithm
from vtkmodules.vtkInteractionWidgets import vtkBoxWidget
from vtkmodules.vtkCommonCore import vtkInformation
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.util.vtkConstants import VTK_OBJECT
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkRenderingCore import vtkRenderWindowInteractor, vtkActor, vtkRenderer, vtkPolyDataMapper
from vtkmodules.vtkFiltersGeneral import vtkTransformPolyDataFilter
from vtkmodules.vtkFiltersCore import vtkAppendPolyData
from vtkmodules.util.misc import calldata_type
from vtkmodules.util import keys
from PyQt5.QtCore import QUuid

from typing import Callable
from time import time

ID_KEY = keys.MakeKey(keys.StringKey, 'id', "vtkActor")

class PrintPlatter(VTKPythonAlgorithmBase):
    def __init__(self) -> None:
        VTKPythonAlgorithmBase.__init__(
            self, nInputPorts=1, inputType='vtkPolyData', nOutputPorts=1, outputType='vtkPolyData')

    def FillInputPortInformation(self, port: int, info: vtkInformation) -> None:
        if port == 0:
            info.Set(vtkAlgorithm.INPUT_IS_REPEATABLE(), 1)
            info.Set(vtkAlgorithm.INPUT_IS_OPTIONAL(), 1)
        return 1

    def RequestData(self, request: str, inInfo: vtkInformation, outInfo: vtkInformation) -> bool:

        n_object = inInfo[0].GetNumberOfInformationObjects()

        if n_object > 0:
            append_f = vtkAppendPolyData()
            append_f.UserManagedInputsOff()
            for i in range(n_object):
                i_info = inInfo[0].GetInformationObject(i)
                input_poly = vtkPolyData.GetData(i_info)
                append_f.AddInputData(input_poly)

            append_f.Update()

            output = vtkPolyData.GetData(outInfo)
            output.ShallowCopy(append_f.GetOutput())

        return 1


class PrintObject(VTKPythonAlgorithmBase):
    def __init__(self) -> None:
        VTKPythonAlgorithmBase.__init__(
            self, nInputPorts=1, inputType='vtkPolyData', nOutputPorts=1, outputType='vtkPolyData')

        self._actor = vtkActor()

        self.id = QUuid.createUuid().toString()
        self.initialised = False

        info = vtkInformation()
        info.Set(ID_KEY, self.id)
        self._actor.GetProperty().SetInformation(info)

    @property
    def actor(self) -> vtkActor:
        return self._actor

    def RequestData(self, request: str, inInfo: vtkInformation, outInfo: vtkInformation) -> bool:
        input_poly = vtkPolyData.GetData(inInfo[0])

        if not self.initialised:
            mapper = vtkPolyDataMapper()
            mapper.AddInputDataObject(input_poly)
            self._actor.SetMapper(mapper)
            self.initialised = True

        output = vtkPolyData.GetData(outInfo)

        transform = vtkTransform()
        transform.SetMatrix(self._actor.GetMatrix())

        coord_converter = vtkTransformPolyDataFilter()
        coord_converter.SetTransform(transform)
        coord_converter.AddInputData(input_poly)
        coord_converter.Update()
        output.ShallowCopy(coord_converter.GetOutput())

        return 1
