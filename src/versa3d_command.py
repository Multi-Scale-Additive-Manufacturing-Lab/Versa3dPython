from PyQt5.QtWidgets import QUndoCommand
import vtk
from src.print_platter import print_object

class import_command(QUndoCommand):
    def __init__(self, path, platter, parent = None):
        super().__init__(parent)
        reader = vtk.vtkSTLReader()
        reader.SetFileName(path)
        reader.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        self._obj = print_object('import', actor)
        self._platter = platter

    def redo(self):
        self._platter.add_parts(self._obj)
    
    def undo(self):
        pass

class translation_command(QUndoCommand):
    def __init__(self, delta_pos, actor, parent = None):
        """
        Translation command                
        Arguments:
            QUndoCommand {QUndoCommand} -- Qt Undo Command class
            delta_pos {ndarray} -- numpy array of delta 
            actor {vtkactor} -- vtk actor class
        """
        super().__init__(parent)
        self._delta_pos = delta_pos
        self._actor = actor

    def redo(self):
        self._actor.AddPosition(self._delta_pos)

    def undo(self):
        self._actor.AddPosition(-self._delta_pos)
