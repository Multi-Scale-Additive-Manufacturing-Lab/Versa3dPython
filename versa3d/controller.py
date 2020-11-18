from PyQt5.QtCore import QObject
from PyQt5 import QtWidgets
import vtk
import versa3d.print_platter as ppl
import versa3d.versa3d_command as vscom
from versa3d.settings import Versa3dSettings
#from versa3d.tool_path_planner import ToolPathGenerator


class Versa3dController(QObject):

    def __init__(self, renderer, parent = None):
        super().__init__(parent = parent)
        self.parent = parent
        self.renderer = renderer
        #self.mem = Memory(location = self.cache_dir.name)
        #self.slicing_pipeline = self.mem.cache(slicing_pipeline)

        #self.settings = Versa3dSettings()

        self.print_objects = {}
        self.platter = vtk.vtkAppendPolyData()
        self.platter.UserManagedInputsOff()

        self.undo_stack = QtWidgets.QUndoStack(self)
        self.undo_stack.setUndoLimit(10)
    
    def add_part(self, idx, obj):
        self.print_objects[idx] = obj
        self.platter.AddInputData(obj.GetOutputDataObject(0))
    
    def remove_part(self, idx):
        obj = self.print_objects.pop(idx)
        self.platter.RemoveInputData(obj.GetOutputDataObject(0))
        return obj
    
    def update_setting(self, printer, param, printhead):
        pass
    
    def setup_pipeline(self):
        pass
        #self.platter = vtk.vtkAppendPolyData()
        #self.voxelizer =  Voxelizer()

        #self.voxelizer.SetInputConnection(self.platter.GetOutputPort())

        #self.tool_path_gen = ToolPathPlanner()
        #self.tool_path_gen.SetInputConnection(self.tool_path_gen.GetOutputPort())

    def reset_picked(self):
        for _ , part in self.print_objects.items():
            if(part.picked):
                part.unpick()

    def import_object(self, filename):
        if(filename[0] != ''):
            com = vscom.ImportCommand(filename[0], self.renderer, self)
            self.undo_stack.push(com)

    def translate(self, delta_pos):
        parts = self.print_objects
        for _, part in parts.items():
            if part.picked:
                com = vscom.TranslationCommand(delta_pos, part.actor)
                self.undo_stack.push(com)
                self.renderer.GetRenderWindow().Render()
    
    def slice_object(self):
        pass

    
        