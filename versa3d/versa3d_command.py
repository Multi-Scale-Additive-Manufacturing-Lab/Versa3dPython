import os

from PyQt5.QtWidgets import QUndoCommand
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkRenderingCore import vtkActor
from versa3d.print_platter import PrintObject
from typing import Callable

from numpy import ndarray

class ImportCommand(QUndoCommand):
    def __init__(self, print_object: PrintObject, cb: Callable[[PrintObject, bool], None], parent: QUndoCommand = None) -> None:
        """[summary]

        Args:
            print_object (PrintObject): print object
            cb (Callable[[PrintObject, bool], None]): callback
            parent (QUndoCommand, optional): Defaults to None.
        """
        super().__init__(parent)
        self._obj = print_object
        self._cb = cb

    def redo(self):
        self._cb(self._obj, True)

    def undo(self):
        self._cb(self._obj, False)

class TransformCommand(QUndoCommand):
    def __init__(self, current: vtkTransform, prev: vtkTransform, actor: vtkActor, parent: QUndoCommand = None) -> None:
        """[summary]

        Args:
            transform_matrix (vtkTransform): transformation matrix
            cb (Callable[[vtkTransform], None]): call back to apply transform
            parent (QUndoCommand, optional): parent undo command. Defaults to None.
        """
        super().__init__(parent)
        self._current = current
        self._prev = prev
        self._actor = actor
        self._exec_first = True

    def redo(self):
        self._actor.SetUserTransform(self._current)

    def undo(self):
        self._actor.SetUserTransform(self._prev)