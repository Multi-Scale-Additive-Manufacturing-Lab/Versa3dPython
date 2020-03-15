from PyQt5.QtWidgets import QUndoCommand
import vtk
from versa3d.print_platter import PrintObject


class ImportCommand(QUndoCommand):
    def __init__(self, path, platter, parent=None):
        """[summary]

        Arguments:
            QUndoCommand {QUndoCommand} -- Qt Undo command class
            path {string} -- file path
            platter {print_platter} -- print platter object

        Keyword Arguments:
            parent {QObject} -- Not used (default: {None})
        """
        super().__init__(parent)
        reader = vtk.vtkSTLReader()
        reader.SetFileName(path)
        reader.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        self._obj = PrintObject('import', actor)
        self._platter = platter

    def redo(self):
        self._platter.add_parts(self._obj)

    def undo(self):
        self._platter.remove_part(self._obj)


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
