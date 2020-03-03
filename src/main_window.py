# -*- coding: utf-8 -*

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import vtk
from vtk.util import numpy_support
import numpy as np
from src.versa3d_settings import load_settings, save_settings
from src.mouse_interaction import actor_highlight
import src.print_platter as ppl


class MainWindow(QtWidgets.QMainWindow):
    """
    main window
    Arguments:
        QtWidgets {QMainWindow} -- main window
    """

    def __init__(self, ui_file_path):
        super().__init__()
        self.ui = uic.loadUi(ui_file_path, self)

        self.settings = load_settings(self)

        self.stl_renderer = vtk.vtkRenderer()
        self.ui.vtkWidget.GetRenderWindow().AddRenderer(self.stl_renderer)

        self.stl_interactor = self.ui.vtkWidget.GetRenderWindow().GetInteractor()

        self.platter = ppl.print_platter()
        self.platter.signal_add_part.connect(self.add_parts)

        style = vtk.vtkInteractorStyleRubberBand3D()
        self.stl_interactor.SetInteractorStyle(style)

        actor_highlight_obs = actor_highlight(self)

        style.AddObserver('SelectionChangedEvent', actor_highlight_obs)

        x_sc = self.settings.value('basic_printer/bed_x', 50, type=float)
        y_sc = self.settings.value('basic_printer/bed_y', 50, type=float)
        z_sc = self.settings.value('basic_printer/bed_z', 100, type=float)

        self.setup_scene((x_sc, y_sc, z_sc))
        self.platter.set_up_dummy_sphere()

        self.stl_interactor.Initialize()

        self.undo_stack = QtWidgets.QUndoStack(self)
        self.undo_stack.setUndoLimit(10)

    @pyqtSlot(vtk.vtkActor)
    def add_parts(self, vtk_actor):
        self.stl_renderer.AddActor(vtk_actor)

    def setup_scene(self, size):
        """set grid scene

        Arguments:
            size {array(3,)} -- size of scene
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
