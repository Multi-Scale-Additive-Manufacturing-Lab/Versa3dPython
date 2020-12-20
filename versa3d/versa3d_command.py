import os

from PyQt5.QtWidgets import QUndoCommand
from PyQt5.QtCore import QUuid
import vtk
from versa3d.print_platter import PrintObject
from typing import List, Callable


class ImportCommand(QUndoCommand):
    def __init__(self, path: str, add: Callable, remove: Callable, parent: QUndoCommand = None):
        """[summary]

        Arguments:
            QUndoCommand {QUndoCommand} -- Qt Undo command class
            path {string} -- file path
            print_platter {PrintPlatterSource} -- print platter object

        Keyword Arguments:
            parent {QObject} -- Not used (default: {None})
        """
        super().__init__(parent)
        _, name = os.path.split(path)
        reader = vtk.vtkSTLReader()
        reader.SetFileName(path)
        reader.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())
        self.actor = vtk.vtkActor()
        self.actor.SetMapper(self._mapper)

        self._obj = PrintObject(reader)
        self._add = add
        self._remove = remove

    def redo(self):
        self._add(self._obj.id, self._obj)

    def undo(self):
        self._remove(self._obj.id)


class TranslationCommand(QUndoCommand):
    def __init__(self, delta_pos: List[float], idx: str, move: Callable, parent: QUndoCommand = None):
        """
        Translation command                
        Arguments:
            QUndoCommand {QUndoCommand} -- Qt Undo Command class
            delta_pos {ndarray} -- numpy array of delta 
            actor {vtkactor} -- vtk actor class
        """
        super().__init__(parent)
        self._delta_pos = delta_pos
        self._id = idx
        self._move = move

    def redo(self):
        self._move(self._id, self._delta_pos)

    def undo(self):
        self._move(self._id, -self._delta_pos)
