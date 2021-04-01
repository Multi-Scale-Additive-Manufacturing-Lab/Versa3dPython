import os

from PyQt5.QtWidgets import QUndoCommand
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkRenderingCore import vtkProp3D
from typing import Callable, List

from numpy import ndarray

class ImportCommand(QUndoCommand):
    def __init__(self, print_object: 'PrintObject', platter : 'PrintPlatter', parent: QUndoCommand = None) -> None:
        super().__init__(parent)
        self._obj = print_object
        self._pl = platter

    def redo(self):
        self._pl.add_part(self._obj)

    def undo(self):
        self._pl.remove_part(self._obj)

class TransformCommand(QUndoCommand):
    def __init__(self, trs: vtkTransform, ls_obj: List['PrintObject'], parent: QUndoCommand = None) -> None:
        super().__init__(parent)
        self._current = trs
        self._ls_obj = ls_obj

    def redo(self):
        for obj in self._ls_obj:
            obj.push_transform(self._current)

    def undo(self):
        for obj in self._ls_obj:
            obj.pop_transform()
