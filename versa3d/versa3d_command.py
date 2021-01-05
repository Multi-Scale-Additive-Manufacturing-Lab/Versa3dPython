import os

from PyQt5.QtWidgets import QUndoCommand
import vtk
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


class TranslationCommand(QUndoCommand):
    def __init__(self, print_object: PrintObject, delta_pos: ndarray, cb: Callable[[PrintObject, ndarray], None], parent: QUndoCommand = None):
        """[summary]

        Args:
            print_object (PrintObject): print object
            delta_pos (ndarray): translation vector
            cb (Callable[[PrintObject, ndarray], None]): callback
            parent (QUndoCommand, optional): Defaults to None.
        """
        super().__init__(parent)
        self._delta_pos = delta_pos
        self._obj = print_object
        self._cb = cb

    def redo(self):
        self._cb(self._obj, self._delta_pos)

    def undo(self):
        self._cb(self._obj, -self._delta_pos)
