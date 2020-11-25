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

        self.controller.settings.add_printer_signal.connect(self.populate_printer_drop_down)
        self.controller.settings.add_printhead_signal.connect(self.populate_printhead_drop_down)
        self.controller.settings.add_parameter_preset_signal.connect(self.populate_preset_drop_down)

        self.controller.load_settings()

        # self.initialize_tab()

    def import_object(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Open stl', "", "stl (*.stl)")
        self.controller.import_object(filename)

    def move_object_y(self):
        y = self.y_delta.value()
        self.controller.translate(np.array([0, y, 0]))

    def move_object_x(self):
        x = self.x_delta.value()
        self.controller.translate(np.array([x, 0, 0]))
    
    def show_printer_window(self):
        self.show_settings_window('printer')
    
    def show_param_window(self):
        self.show_settings_window('parameter_preset')
    
    def show_printhead_window(self):
        self.show_settings_window('printhead')
    
    def show_settings_window(self, type_string):
        win = SettingsWindow(self.controller, type_string, self)
        win.show()
    
    @pyqtSlot(str)
    def populate_printer_drop_down(self, value):
        self.printer_cmb_box.addItem(value)
    
    @pyqtSlot(str)
    def populate_printhead_drop_down(self, value):
        self.printhead_cmb_box.addItem(value)
    
    @pyqtSlot(str)
    def populate_preset_drop_down(self, value):
        self.print_settings_cmb_box.addItem(value)
    
    # TODO implement undo for list
    # @pyqtSlot(ppl.PrintObject)
    # def add_obj_to_list(self, obj):
    #    table = self.table_stl
    #    name = obj.name
    #    table.insertRow(table.rowCount())

    #    name_entry = QtWidgets.QTableWidgetItem(name)
    #    scale_value = QtWidgets.QTableWidgetItem(str(1.0))
    #    copies_value = QtWidgets.QTableWidgetItem(str(1.0))

    #    current_row = table.rowCount() - 1
    #    table.setItem(current_row, 0, name_entry)
    #    table.setItem(current_row, 1, copies_value)
    #    table.setItem(current_row, 2, scale_value)

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
