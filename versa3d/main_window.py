# -*- coding: utf-8 -*

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5 import QtGui
import vtk
from vtk.util import numpy_support
import numpy as np
from versa3d.mouse_interaction import ActorHighlight
from versa3d.controller import Versa3dController
from versa3d.settings_window import SettingsWindow
from versa3d.settings import SettingTypeKey


class MainWindow(QtWidgets.QMainWindow):
    """Main Window

    Args:
        QtWidgets (QMainWindow): main window
    """

    def __init__(self, ui_file_path):
        super().__init__()
        uic.loadUi(ui_file_path, self)

        self.stl_renderer = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.stl_renderer)

        self.stl_interactor = self.vtkWidget.GetRenderWindow().GetInteractor()

        self.controller = Versa3dController(self.stl_renderer, self)

        style = vtk.vtkInteractorStyleRubberBand3D()
        self.stl_interactor.SetInteractorStyle(style)

        actor_highlight_obs = ActorHighlight(
            self.stl_renderer, self.controller)

        style.AddObserver('SelectionChangedEvent', actor_highlight_obs)

        self.setup_scene((50, 50, 100))

        self.stl_interactor.Initialize()

        self.push_button_x.clicked.connect(self.move_object_x)
        self.push_button_y.clicked.connect(self.move_object_y)

        self.push_button_mod_print_settings.clicked.connect(self.show_param_window)
        self.push_button_mod_printer.clicked.connect(self.show_printer_window)
        self.push_button_mod_printhead.clicked.connect(self.show_printhead_window)

        self.action_import_stl.triggered.connect(self.import_object)

        self.action_undo.triggered.connect(self.controller.undo_stack.undo)
        self.action_redo.triggered.connect(self.controller.undo_stack.redo)

        self.printer_cmb_box.currentIndexChanged.connect(self.controller.change_printer)
        self.printhead_cmb_box.currentIndexChanged.connect(self.controller.change_printhead)
        self.print_settings_cmb_box.currentIndexChanged.connect(self.controller.change_preset)

        self.controller.settings.add_setting_signal.connect(self.populate_printer_drop_down)

        self.ExportGCodeButton.clicked.connect(self.export_gcode)
        self.controller.load_settings()
    
    @pyqtSlot()
    def export_gcode(self):
        filename = QtWidgets.QFileDialog.getSaveFileName(
            self, 'Save Gcode', "", "zip (*.zip)")
        if len(filename) != 0 or not filename is None:
            self.controller.export_gcode(filename[0])

    @pyqtSlot()
    def import_object(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Open stl', "", "stl (*.stl)")
        if len(filename) != 0 or not filename is None:
            self.controller.import_object(filename[0], filename[1])

    def move_object_y(self):
        y = self.y_delta.value()
        self.controller.translate(np.array([0, y, 0], dtype=float))

    def move_object_x(self):
        x = self.x_delta.value()
        self.controller.translate(np.array([x, 0, 0], dtype=float))
    
    def show_printer_window(self):
        self.show_settings_window(self.printer_cmb_box, 'printer')
    
    def show_param_window(self):
        self.show_settings_window(self.print_settings_cmb_box, 'parameter_preset')
    
    def show_printhead_window(self):
        self.show_settings_window(self.printhead_cmb_box, 'printhead')
    
    def show_settings_window(self, slave_cmb, type_string):
        win = SettingsWindow(slave_cmb, self.controller, type_string, self)
        win.exec()
    
    @pyqtSlot(str, str)
    def populate_printer_drop_down(self, setting_type, value):
        if(setting_type == SettingTypeKey.printer.value):
            self.printer_cmb_box.addItem(value)
        elif(setting_type == SettingTypeKey.printhead.value):
            self.printhead_cmb_box.addItem(value)
        elif(setting_type == SettingTypeKey.print_param.value):
            self.print_settings_cmb_box.addItem(value)

    def setup_scene(self, size):
        """set grid scene

        Args:
            size (array(3,)): size of scene
        """
        colors = vtk.vtkNamedColors()

        self.stl_renderer.SetBackground(colors.GetColor3d("lightslategray"))

        # add coordinate axis
        axes_actor = vtk.vtkAxesActor()
        axes_actor.SetShaftTypeToLine()
        axes_actor.SetTipTypeToCone()

        axes_actor.SetTotalLength(*size)

        number_grid = 50

        X = numpy_support.numpy_to_vtk(np.linspace(0, size[0], number_grid))
        Y = numpy_support.numpy_to_vtk(np.linspace(0, size[1], number_grid))
        Z = numpy_support.numpy_to_vtk(np.array([0]*number_grid))

        # set up grid
        grid = vtk.vtkRectilinearGrid()
        grid.SetDimensions(number_grid, number_grid, number_grid)
        grid.SetXCoordinates(X)
        grid.SetYCoordinates(Y)
        grid.SetZCoordinates(Z)

        geometry_filter = vtk.vtkRectilinearGridGeometryFilter()
        geometry_filter.SetInputData(grid)
        geometry_filter.SetExtent(
            0, number_grid - 1, 0, number_grid - 1, 0, number_grid - 1)
        geometry_filter.Update()

        grid_mapper = vtk.vtkPolyDataMapper()
        grid_mapper.SetInputConnection(geometry_filter.GetOutputPort())

        grid_actor = vtk.vtkActor()
        grid_actor.SetMapper(grid_mapper)
        grid_actor.GetProperty().SetRepresentationToWireframe()
        grid_actor.GetProperty().SetColor(colors.GetColor3d('Banana'))
        grid_actor.GetProperty().EdgeVisibilityOn()
        grid_actor.SetPickable(False)
        grid_actor.SetDragable(False)

        self.stl_renderer.AddActor(axes_actor)
        self.stl_renderer.AddActor(grid_actor)
        self.stl_renderer.ResetCamera()
