from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5 import QtWidgets
import vtk
import versa3d.print_platter as ppl
import versa3d.versa3d_command as vscom
from versa3d.settings import Versa3dSettings
from versa3d.slicing import VoxelSlicer
from versa3d.tool_path_planner import ToolPathPlannerFilter


class Versa3dController(QObject):

    def __init__(self, renderer, parent = None):
        super().__init__(parent = parent)
        self.parent = parent
        self.renderer = renderer

        self._settings = Versa3dSettings()
        
        self.print_objects = {}
        self.platter = vtk.vtkAppendPolyData()
        self.platter.UserManagedInputsOff()

        self.undo_stack = QtWidgets.QUndoStack(self)
        self.undo_stack.setUndoLimit(10)

        self._printer_idx = 0
        self._printhead_idx = 0
        self._parameter_preset_idx = 0

        self.setup_pipeline()
    
    @property
    def settings(self):
        return self._settings

    @pyqtSlot(int)
    def change_printer(self, idx):
        self._printer_idx = idx
    
    @pyqtSlot(int)
    def change_printhead(self, idx):
        self._printhead_idx = idx
    
    @pyqtSlot(int)
    def change_preset(self, idx):
        self._parameter_preset_idx = idx
        
    def load_settings(self):
        self.settings.load_all()
    
    def add_part(self, idx, obj):
        self.print_objects[idx] = obj
        self.platter.AddInputData(obj.GetOutputDataObject(0))
        self.renderer.AddActor(obj.actor)
        self.renderer.GetRenderWindow().Render()
    
    def remove_part(self, idx):
        obj = self.print_objects.pop(idx)
        self.platter.RemoveInputData(obj.GetOutputDataObject(0))
        self.renderer.RemoveActor(obj.actor)
        self.renderer.GetRenderWindow().Render()
        return obj
    
    def move_part(self, idx, position):
        actor = self.print_objects[idx].actor
        actor.AddPosition(position)
        self.renderer.GetRenderWindow().Render()
    
    def export_gcode(self, file_path):
        printer_setting = self.settings.get_printer(self._printer_idx)
        printhead_setting = self.settings.get_printhead(self._printhead_idx)
        param_setting = self.settings.get_parameter_preset(self._parameter_preset_idx)
        self.slice_object()
        self.tool_path_gen.set_settings(printer_setting, printhead_setting, param_setting)
        self.tool_path_gen.Update()
        self.tool_path_gen.write(file_path)
    
    def setup_pipeline(self):
        self.voxelizer =  VoxelSlicer()
        self.voxelizer.SetInputConnection(self.platter.GetOutputPort())
        self.tool_path_gen = ToolPathPlannerFilter()
        self.tool_path_gen.SetInputConnection(self.voxelizer.GetOutputPort())

    def reset_picked(self):
        for part in self.print_objects.values():
            if(part.picked):
                part.unpick()

    def import_object(self, filename):
        if(filename[0] != ''):
            com = vscom.ImportCommand(filename[0], self.add_part, self.remove_part)
            self.undo_stack.push(com)

    def translate(self, delta_pos):
        parts = self.print_objects
        for idx, part in parts.items():
            if part.picked:
                com = vscom.TranslationCommand(delta_pos, idx, self.move_part)
                self.undo_stack.push(com)
    
    @pyqtSlot()
    def slice_object(self):
        printer_setting = self.settings.get_printer(self._printer_idx)
        printhead_setting = self.settings.get_printhead(self._printhead_idx)
        param_setting = self.settings.get_parameter_preset(self._parameter_preset_idx)
        self.voxelizer.set_settings(printer_setting, printhead_setting, param_setting)
        self.voxelizer.Update()

    
        