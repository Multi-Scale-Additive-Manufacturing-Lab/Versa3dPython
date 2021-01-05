import os

from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5 import QtWidgets
import vtk
import versa3d.print_platter as ppl
import versa3d.versa3d_command as vscom
from versa3d.settings import Versa3dSettings
from versa3d.slicing import VoxelSlicer
from versa3d.tool_path_planner import ToolPathPlannerFilter
from versa3d.print_platter import PrintObject

from numpy import ndarray


def reader_factory(f_path: str, ext: str) -> vtk.vtkAbstractPolyDataReader:
    if ext.lower() == 'stl (*.stl)':
        reader = vtk.vtkSTLReader()
        reader.SetFileName(f_path)
        reader.Update()
        return reader
    else:
        raise ValueError('Extension not supported : {}' % (ext))


class Versa3dController(QObject):

    def __init__(self, renderer: vtk.vtkRenderer, parent: QObject = None) -> None:
        super().__init__(parent=parent)
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
    def settings(self) -> None:
        return self._settings

    @pyqtSlot(int)
    def change_printer(self, idx: str) -> None:
        self._printer_idx = idx

    @pyqtSlot(int)
    def change_printhead(self, idx: str) -> None:
        self._printhead_idx = idx

    @pyqtSlot(int)
    def change_preset(self, idx: str) -> None:
        self._parameter_preset_idx = idx

    def load_settings(self) -> None:
        self.settings.load_all()

    def import_callback(self, obj: PrintObject, mode=True) -> None:
        if mode:
            self.print_objects[obj.id] = obj
            self.platter.AddInputData(obj.GetOutputDataObject(0))
            obj.render(self.renderer)
        else:
            obj = self.print_objects.pop(obj.id)
            self.platter.RemoveInputData(obj.GetOutputDataObject(0))
            obj.unrender(self.renderer)

    def translate_callback(self, obj: PrintObject, vec: ndarray) -> None:
        if vec.ndim != 1:
            raise ValueError('Invalid dimension : {%d}' % (vec.ndim))

        if len(vec) != 3:
            raise ValueError('Invalid length : {%d}' % (len(vec)))

        obj.move(vec[0], vec[1], vec[2])
        obj.Update()
        obj.render(self.renderer)

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

    def reset_picked(self) -> None:
        for part in self.print_objects.values():
            if(part.picked):
                part.unpick()

    def import_object(self, filename: str, ext: str) -> None:
        if(filename != ''):
            obj_src = reader_factory(filename, ext)

            obj = PrintObject()
            obj.SetInputConnection(obj_src.GetOutputPort())
            obj.Update()

            com = vscom.ImportCommand(obj, self.import_callback)
            self.undo_stack.push(com)

    def translate(self, delta_pos: ndarray) -> None:
        parts = self.print_objects
        for part in parts.values():
            if part.picked:
                com = vscom.TranslationCommand(
                    part, delta_pos, self.translate_callback)
                self.undo_stack.push(com)

    @pyqtSlot()
    def slice_object(self) -> None:
        printer_setting = self.settings.get_printer(self._printer_idx)
        printhead_setting = self.settings.get_printhead(self._printhead_idx)
        param_setting = self.settings.get_parameter_preset(
            self._parameter_preset_idx)
        self.voxelizer.set_settings(
            printer_setting, printhead_setting, param_setting)
        self.voxelizer.Update()
