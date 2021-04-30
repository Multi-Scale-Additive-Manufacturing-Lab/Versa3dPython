__author__ = "Marc Wang"
__copyright__ = "Copyright (c) 2021 MSAM Lab - University of Waterloo"
__license__ = "BSD-3-Clause"
__maintainer__ = "Marc Wang"
__email__ = "marc.wang@uwaterloo.ca"


from PyQt5.QtWidgets import QUndoCommand
from vtkmodules.vtkCommonTransforms import vtkTransform
from typing import List

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
