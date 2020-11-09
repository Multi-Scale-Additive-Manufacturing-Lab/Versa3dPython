import os

from PyQt5.QtWidgets import QUndoCommand
from PyQt5.QtCore import QUuid
import vtk
from versa3d.print_platter import PrintPlatterSource, PrintObject


class ImportCommand(QUndoCommand):
    def __init__(self, path, renderer, print_platter, parent=None):
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
        self._obj = PrintObject(name, reader)
        self._platter = print_platter
        self.id = QUuid.createUuid()
        self.renderer = renderer

    def redo(self):
        self._platter.add_part(self.id, self._obj)
        self.renderer.AddActor(self._obj.actor)
        self.renderer.GetRenderWindow().Render()

    def undo(self):
        self._platter.remove_part(self.id)
        self.renderer.RemoveActor(self._obj.actor)
        self.renderer.GetRenderWindow().Render()


class TranslationCommand(QUndoCommand):
    def __init__(self, delta_pos, actor):
        """
        Translation command                
        Arguments:
            QUndoCommand {QUndoCommand} -- Qt Undo Command class
            delta_pos {ndarray} -- numpy array of delta 
            actor {vtkactor} -- vtk actor class
        """
        super().__init__()
        self._delta_pos = delta_pos
        self._actor = actor

    def redo(self):
        self._actor.AddPosition(self._delta_pos)

    def undo(self):
        self._actor.AddPosition(-self._delta_pos)
