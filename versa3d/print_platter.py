import numpy as np
from vtkmodules.util.vtkAlgorithm import VTKPythonAlgorithmBase, vtkAlgorithm
from vtkmodules.vtkInteractionWidgets import vtkBoxWidget
from vtkmodules.vtkCommonCore import vtkInformation, vtkInformationVector
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.util.vtkConstants import VTK_OBJECT
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkRenderingCore import vtkRenderWindowInteractor, vtkActor, vtkRenderer, vtkPolyDataMapper
from vtkmodules.vtkFiltersGeneral import vtkTransformPolyDataFilter
from vtkmodules.vtkFiltersCore import vtkAppendPolyData
from vtkmodules.util.misc import calldata_type
from PyQt5.QtCore import QUuid
from PyQt5.QtWidgets import QUndoStack, QUndoCommand

from typing import Callable
from time import time


class TransformCommand(QUndoCommand):
    def __init__(self, current: vtkTransform, prev: vtkTransform, cb: Callable[[vtkTransform], None], parent: QUndoCommand = None) -> None:
        """[summary]

        Args:
            transform_matrix (vtkTransform): transformation matrix
            cb (Callable[[vtkTransform], None]): call back to apply transform
            parent (QUndoCommand, optional): parent undo command. Defaults to None.
        """
        super().__init__(parent)
        self._current = current
        self._prev = prev
        self._cb = cb
        self._exec_first = True

    def redo(self):
        self._cb(self._current)

    def undo(self):
        self._cb(self._prev)


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
    def __init__(self, undo_stack: QUndoStack) -> None:
        VTKPythonAlgorithmBase.__init__(
            self, nInputPorts=1, inputType='vtkPolyData', nOutputPorts=1, outputType='vtkPolyData')

        self._actor = vtkActor()
        self._actor.AddObserver('StartPickEvent', self.pick)
        self._actor.AddObserver('EndPickEvent', self.unpick)

        self._box_widget = vtkBoxWidget()
        self._box_widget.TranslationEnabledOn()
        self._box_widget.RotationEnabledOn()
        self._box_widget.ScalingEnabledOff()
        self._box_widget.SetProp3D(self._actor)
        self._box_widget.PickingManagedOn()
        self._box_widget.SetPlaceFactor(1.50)
        self._box_widget.AddObserver('InteractionEvent', self.box_sync)
        self._box_widget.AddObserver('StartInteractionEvent', self.save_state)
        self._box_widget.AddObserver('EndInteractionEvent', self.commit_state)

        self.picked = False
        self._backup_prop = None
        self.id = QUuid.createUuid().toString()
        self.initialised = False

        self.import_command = None
        self.undo_stack = undo_stack

        self.prev_state = vtkTransform()
        self._box_widget.GetTransform(self.prev_state)

    def save_state(self, caller: vtkBoxWidget, ev: str):
        new_state = vtkTransform()
        caller.GetTransform(new_state)
        self.prev_state = new_state

    def commit_state(self, caller: vtkBoxWidget, ev: str):
        new_state = vtkTransform()
        caller.GetTransform(new_state)
        com = TransformCommand(new_state, self.prev_state,
                               self.set_state, self.import_command)
        self.undo_stack.push(com)

    def set_state(self, trs: vtkTransform):
        self._actor.SetUserTransform(trs)
        self._box_widget.SetTransform(trs)

    def box_sync(self, caller: vtkBoxWidget, ev: str) -> None:
        cur = vtkTransform()
        caller.GetTransform(cur)
        self._actor.SetUserTransform(cur)
        self.Modified()

    @property
    def actor(self) -> vtkActor:
        return self._actor

    @calldata_type(VTK_OBJECT)
    def pick(self, caller: vtkActor, ev: str, interactor: vtkRenderWindowInteractor = None) -> None:
        """set pick status

        Args:
            caller (vtkRenderWindowInteractor): object being observed
            ev (string): event type description
        """
        if not interactor is None:
            self._box_widget.SetInteractor(interactor)
            if not self.picked:
                self._box_widget.On()

    @calldata_type(VTK_OBJECT)
    def unpick(self, caller: vtkActor, ev: str, interactor: vtkRenderWindowInteractor = None) -> None:
        """set pick status

        Args:
            caller (vtkRenderWindowInteractor): object being observed
            ev (string): event type description
        """
        if not interactor is None:
            self._box_widget.SetInteractor(interactor)
            if not self.picked:
                self._box_widget.Off()

    def move(self, x: float, y: float, z: float) -> None:
        self._actor.AddPosition(x, y, z)
        self.Modified()

    def rotate(self, w: float, x: float, y: float, z: float) -> None:
        self._actor.RotateWXYZ(w, x, y, z)
        self.Modified()

    def RequestData(self, request: str, inInfo: vtkInformation, outInfo: vtkInformation) -> bool:
        input_poly = vtkPolyData.GetData(inInfo[0])

        if not self.initialised:
            mapper = vtkPolyDataMapper()
            mapper.AddInputDataObject(input_poly)
            self._actor.SetMapper(mapper)
            self.initialised = True

        self._box_widget.PlaceWidget(self._actor.GetBounds())

        output = vtkPolyData.GetData(outInfo)

        transform = vtkTransform()
        transform.SetMatrix(self._actor.GetMatrix())

        coord_converter = vtkTransformPolyDataFilter()
        coord_converter.SetTransform(transform)
        coord_converter.AddInputData(input_poly)
        coord_converter.Update()
        output.ShallowCopy(coord_converter.GetOutput())

        return 1
