import os
from typing import Tuple

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from PyQt5 import QtWidgets
import vtk
import versa3d.print_platter as ppl
import versa3d.versa3d_command as vscom
from versa3d.settings import Versa3dSettings
from versa3d.slicing import VoxelSlicer
from versa3d.tool_path_planner import ToolPathPlannerFilter
from versa3d.print_platter import PrintObject, PrintPlatter

from numpy import ndarray
from typing import Tuple

def reader_factory(f_path: str, ext: str) -> vtk.vtkAbstractPolyDataReader:
    if ext.lower() == 'stl (*.stl)':
        reader = vtk.vtkSTLReader()
        reader.SetFileName(f_path)
        reader.Update()
        return reader
    else:
        raise ValueError('Extension not supported : {}' % (ext))


class Versa3dController(QObject):
    update_scene = pyqtSignal(float, float, float)
    selection_obj = pyqtSignal(bool, tuple)

    def __init__(self, renderer: vtk.vtkRenderer, parent: QObject = None) -> None:
        super().__init__(parent=parent)
        self.renderer = renderer

        self._settings = Versa3dSettings()

        self.print_objects = {}
        self.platter = PrintPlatter()

        self.undo_stack = QtWidgets.QUndoStack(self)

        self._printer_idx = 0
        self._printhead_idx = 0
        self._parameter_preset_idx = 0

        self.setup_pipeline()

        self._settings.update_printer_signal.connect(
            self.update_scene_listener)

    @pyqtSlot(int, str)
    def update_scene_listener(self, idx: int, attr_key: str):
        if self._printer_idx == idx:
            setting_dict = self._settings.get_printer(idx)
            if attr_key == 'build_bed_size':
                new_size = setting_dict.build_bed_size.value
                self.update_scene.emit(new_size[0], new_size[1], new_size[2])

    @property
    def settings(self) -> None:
        return self._settings

    @pyqtSlot(int)
    def change_printer(self, idx: int) -> None:
        if self._printer_idx != idx:
            self._printer_idx = idx
            printer_setting = self._settings.get_printer(idx)
            new_size = printer_setting.build_bed_size.value
            self.update_scene.emit(new_size[0], new_size[1], new_size[2])

    @pyqtSlot(int)
    def change_printhead(self, idx: int) -> None:
        self._printhead_idx = idx

    @pyqtSlot(int)
    def change_preset(self, idx: int) -> None:
        self._parameter_preset_idx = idx

    def load_settings(self) -> None:
        self.settings.load_all()

    def import_callback(self, obj: PrintObject, mode=True) -> None:
        if mode:
            self.print_objects[obj.id] = obj
            self.platter.SetInputConnection(0, obj.GetOutputPort())
            obj.render(self.renderer)
        else:
            obj = self.print_objects.pop(obj.id)
            self.platter.RemoveInputConnection(0, obj.GetOutputPort())
            obj.unrender(self.renderer)
        
        self.platter.Update()

    def export_gcode(self, file_path: str) -> None:
        printer_setting = self.settings.get_printer(self._printer_idx)
        printhead_setting = self.settings.get_printhead(self._printhead_idx)
        param_setting = self.settings.get_parameter_preset(
            self._parameter_preset_idx)
        self.slice_object()
        self.tool_path_gen.set_settings(
            printer_setting, printhead_setting, param_setting)
        self.tool_path_gen.Update()
        self.tool_path_gen.write(file_path)

    def setup_pipeline(self) -> None:
        self.voxelizer = VoxelSlicer()
        self.voxelizer.SetInputConnection(self.platter.GetOutputPort())
        self.tool_path_gen = ToolPathPlannerFilter()
        self.tool_path_gen.SetInputConnection(self.voxelizer.GetOutputPort())

    def import_object(self, filename: str, ext: str) -> None:
        if(filename != ''):
            obj_src = reader_factory(filename, ext)

            obj = PrintObject(self.undo_stack)
            obj.SetInputConnection(obj_src.GetOutputPort())
            obj.Update()

            com = vscom.ImportCommand(obj, self.import_callback)
            self.undo_stack.push(com)
            obj.import_command = com

    @pyqtSlot(int)
    def transform(self):
        pass
    
    @pyqtSlot(int, tuple)
    def translate(self, idx : int, vec : Tuple[float,float,float]):
        pass

    @pyqtSlot(int, tuple)
    def rotate(self, idx : int, angle : Tuple[float,float,float]):
        pass

    @pyqtSlot()
    def slice_object(self) -> None:
        printer_setting = self.settings.get_printer(self._printer_idx)
        printhead_setting = self.settings.get_printhead(self._printhead_idx)
        param_setting = self.settings.get_parameter_preset(
            self._parameter_preset_idx)
        self.voxelizer.set_settings(
            printer_setting, printhead_setting, param_setting)
        self.voxelizer.Update()
