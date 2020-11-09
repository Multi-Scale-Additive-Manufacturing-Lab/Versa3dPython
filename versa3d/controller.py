import joblib
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5 import QtWidgets
import versa3d.print_platter as ppl
import versa3d.versa3d_command as vscom

class Versa3dController(QObject):

    def __init__(self, renderer, parent = None):
        super().__init__(parent = parent)
        self.parent = parent
        self.renderer = renderer

        self.undo_stack = QtWidgets.QUndoStack(self)
        self.undo_stack.setUndoLimit(10)

        self.platter = ppl.PrintPlatterSource()

    def reset_picked(self):
        for _ , part in self.platter.print_objects.items():
            if(part.picked):
                part.unpick()

    def import_object(self, filename):
        if(filename[0] != ''):
            com = vscom.ImportCommand(filename[0], self.renderer, self.platter)
            self.undo_stack.push(com)

    def translate(self, delta_pos):
        parts = self.platter.print_objects
        for _, part in parts.items():
            if part.picked:
                com = vscom.TranslationCommand(delta_pos, part.actor)
                self.undo_stack.push(com)
                self.renderer.GetRenderWindow().Render()

    
        