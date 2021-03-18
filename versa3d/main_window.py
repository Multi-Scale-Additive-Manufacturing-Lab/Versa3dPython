# -*- coding: utf-8 -*

from typing import Set
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSlot, pyqtSignal
import vtk
from vtkmodules.util.misc import calldata_type
from vtkmodules.util.vtkConstants import VTK_OBJECT
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleRubberBand3D
from vtkmodules.vtkRenderingCore import vtkProp3DCollection, vtkActor
from vtkmodules.vtkCommonTransforms import vtkTransform

from vtkmodules.util import numpy_support
from vtkmodules import vtkInteractionStyle as vtkIntStyle
import numpy as np
from versa3d.controller import Versa3dController
from versa3d.settings_window import SettingsWindow
from versa3d.movement_widget import MovementPanel
from versa3d.settings import SettingTypeKey, SettingWrapper
from versa3d.mouse_interaction import RubberBandHighlight
from versa3d.scene import Versa3dScene


class MainWindow(QtWidgets.QMainWindow):
    """Main Window

    Args:
        QtWidgets (QMainWindow): main window
    """
    
    transform_sig = pyqtSignal(vtkTransform, vtkTransform, vtkActor, str)

    undo_sig = pyqtSignal()
    redo_sig = pyqtSignal()

    import_obj_signal = pyqtSignal(str, str)
    export_gcode_signal = pyqtSignal(str)
    slice_object_signal = pyqtSignal()

    change_printer_signal = pyqtSignal(int)
    change_printhead_signal = pyqtSignal(int)
    change_preset_signal = pyqtSignal(int)

    show_parameter_win = pyqtSignal()
    show_printer_win = pyqtSignal()
    show_printhead_win = pyqtSignal()

    def __init__(self, ui_file_path: str) -> None:
        super().__init__()
        uic.loadUi(ui_file_path, self)

        self.scene = Versa3dScene(self.vtkWidget)
        self.scene.selection_start.connect(self.spawn_movement_win)
        self.scene.selection_end.connect(self.remove_movement_win)

        self.push_button_mod_print_settings.clicked.connect(
            self.show_param_window)
        self.push_button_mod_printer.clicked.connect(self.show_printer_window)
        self.push_button_mod_printhead.clicked.connect(
            self.show_printhead_window)

        self.action_import_stl.triggered.connect(self.import_object)

        self.action_undo.triggered.connect(self.undo_sig)
        self.action_redo.triggered.connect(self.redo_sig)

        self.printer_cmb_box.currentIndexChanged.connect(
            self.change_printer_signal)
        self.printhead_cmb_box.currentIndexChanged.connect(
            self.change_printhead_signal)
        self.print_settings_cmb_box.currentIndexChanged.connect(
            self.change_preset_signal)

        self.ExportGCodeButton.clicked.connect(self.export_gcode)
        self.SliceButton.clicked.connect(self.slice_object_signal)

        self.movement_panel = MovementPanel(self)
        self.object_interaction.insertWidget(1, self.movement_panel)
        self.object_interaction.setCurrentIndex(0)

        self.movement_panel.translate_sig.connect(self.translate_obj)
        #self.movement_panel.rotate_sig.connect(self.rotate_obj)
        #self.movement_panel.scale_sig.connect(self.scale_obj)
        self.scene.selection_pos.connect(self.movement_panel.update_current_position)
    
    @pyqtSlot(float, float, float)
    def translate_obj(self, x : float, y : float, z : float):
        self.scene.rubber_style.set_position(x,y,z)
    
    @pyqtSlot()
    def spawn_movement_win(self) -> None:
        self.object_interaction.setCurrentIndex(1)
    
    @pyqtSlot()
    def remove_movement_win(self) -> None:
        self.object_interaction.setCurrentIndex(0)
        self.movement_panel.reset()
        self.selected_obj = None

    @pyqtSlot()
    def export_gcode(self) -> None:
        filename = QtWidgets.QFileDialog.getSaveFileName(
            self, 'Save Gcode', "", "zip (*.zip)")
        if len(filename[0]) != 0 and not filename[0] is None:
            self.export_gcode_signal.emit(filename[0])

    @pyqtSlot()
    def import_object(self) -> None:
        filename = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Open stl', "", "stl (*.stl)")
        if len(filename[0]) != 0 and not filename is None:
            self.import_obj_signal.emit(filename[0], filename[1])

    @pyqtSlot()
    def show_printer_window(self) -> None:
        self.show_printer_win.emit()

    @pyqtSlot()
    def show_param_window(self) -> None:
        self.show_parameter_win.emit()

    @pyqtSlot()
    def show_printhead_window(self) -> None:
        self.show_printhead_win.emit()

    @pyqtSlot(SettingWrapper)
    def spawn_setting_window(self, val : SettingWrapper) -> None:
        win = SettingsWindow(self.print_settings_cmb_box, val, self)
        win.exec()
    
    @pyqtSlot(SettingWrapper)
    def spawn_printer_window(self, val : SettingWrapper) -> None:
        win = SettingsWindow(self.printer_cmb_box, val, self)
        win.exec()
    
    @pyqtSlot(SettingWrapper)
    def spawn_printhead_window(self, val : SettingWrapper) -> None:
        win = SettingsWindow(self.printhead_cmb_box, val, self)
        win.exec()

    @pyqtSlot(str, str)
    def populate_printer_drop_down(self, setting_type: str, value: str) -> None:
        if(setting_type == SettingTypeKey.printer.value):
            self.printer_cmb_box.addItem(value)
        elif(setting_type == SettingTypeKey.printhead.value):
            self.printhead_cmb_box.addItem(value)
        elif(setting_type == SettingTypeKey.print_param.value):
            self.print_settings_cmb_box.addItem(value)
