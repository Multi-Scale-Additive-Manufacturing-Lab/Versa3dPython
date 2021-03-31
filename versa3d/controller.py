import os
from typing import Tuple

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from PyQt5 import QtWidgets
import vtk
from vtkmodules.vtkRenderingCore import vtkActor, vtkImageActor, vtkPolyDataMapper
from vtkmodules.vtkCommonTransforms import vtkTransform
import versa3d.print_platter as ppl
import versa3d.versa3d_command as vscom
from versa3d.settings import Versa3dSettings, SettingWrapper
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

    spawn_preset_win_signal = pyqtSignal(SettingWrapper)
    spawn_printer_win_signal = pyqtSignal(SettingWrapper)
    spawn_printhead_win_signal = pyqtSignal(SettingWrapper)

    def __init__(self, parent: QObject = None) -> None:
        super().__init__(parent=parent)

        self._settings = Versa3dSettings()

        self.print_plate = PrintPlatter(self)

        self.undo_stack = QtWidgets.QUndoStack(self)

        self._printer_idx = 0
        self._printhead_idx = 0
        self._parameter_preset_idx = 0

        self._settings.update_printer_signal.connect(
            self.update_scene_listener)

        self.update_scene.connect(self.print_plate.resize_scene)
        self.print_plate.command_sig.connect(self.push_command)

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
    
    @property
    def printer_idx(self) -> int:
        return self._printer_idx
    
    @printer_idx.setter
    def printer_idx(self, idx : int):
        if self._printer_idx != idx:
            self._printer_idx = idx
            printer_setting = self._settings.get_printer(idx)
            new_size = printer_setting.build_bed_size.value
            self.update_scene.emit(new_size[0], new_size[1], new_size[2])
        
    @pyqtSlot(int)
    def change_printer(self, idx: int) -> None:
        self.printer_idx = idx

    @pyqtSlot(int)
    def change_printhead(self, idx: int) -> None:
        self._printhead_idx = idx

    @pyqtSlot(int)
    def change_preset(self, idx: int) -> None:
        self._parameter_preset_idx = idx
    
    @pyqtSlot()
    def edit_printer(self) -> None:
        printer_setting = self._settings.printer
        cb_obj = SettingWrapper(printer_setting, 
                        self._settings.clone_printer,
                        self._settings.remove_printer,
                        self._settings.save_printer)
        self.spawn_printer_win_signal.emit(cb_obj)
    
    @pyqtSlot()
    def edit_printhead(self) -> None:
        printhead_setting = self._settings.printhead
        cb_obj = SettingWrapper(printhead_setting, 
                        self._settings.clone_printhead,
                        self._settings.remove_printhead,
                        self._settings.save_printhead)
        self.spawn_printhead_win_signal.emit(cb_obj)
    
    @pyqtSlot()
    def edit_preset(self) -> None:
        param_setting = self._settings.parameter_preset
        cb_obj = SettingWrapper(param_setting, 
                        self._settings.clone_parameter_preset,
                        self._settings.remove_parameter_preset,
                        self._settings.save_parameter_preset)
        self.spawn_preset_win_signal.emit(cb_obj)

    def load_settings(self) -> None:
        self.settings.load_all()

    @pyqtSlot(str)
    def export_gcode(self, file_path: str) -> None:
        # TODO reconnect gcode export later
        pass

    @pyqtSlot(str, str)
    def import_object(self, filename: str, ext: str) -> None:
        if(filename != ''):
            obj_src = reader_factory(filename, ext)
            self.print_plate.import_part(obj_src)

    @pyqtSlot(QtWidgets.QUndoCommand)
    def push_command(self, com : QtWidgets.QUndoCommand):
        self.undo_stack.push(com)

    @pyqtSlot()
    def slice_object(self) -> None:
        printer_setting = self.settings.get_printer(self._printer_idx)
        printhead_setting = self.settings.get_printhead(self._printhead_idx)
        param_setting = self.settings.get_parameter_preset(
            self._parameter_preset_idx)

        for obj in self.print_plate.values():
            obj.slice_obj(printer_setting, printhead_setting, param_setting)
            self.render_sl_signal.emit(obj)