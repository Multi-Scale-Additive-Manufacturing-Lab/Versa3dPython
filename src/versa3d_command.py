from PyQt5.QtWidgets import QUndoCommand
import vtk


class translation_command(QUndoCommand):
    def __init__(self, delta_pos, actor):
        super().__init__()
        self._delta_pos = delta_pos
        self._actor = actor

    def redo(self):
        self._actor.AddPosition(self._delta_pos)

    def undo(self):
        self._actor.AddPosition(-self._delta_pos)
