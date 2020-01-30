# -*- coding: utf-8 -*

from PyQt5 import QtWidgets, uic
import numpy as np
import vtk
from vtk.util import numpy_support


class MainWindow(QtWidgets.QMainWindow):
    """
    main window
    Arguments:
        QtWidgets {QMainWindow} -- main window
    """

    def __init__(self, ui_file_path):
        super().__init__()
        self.ui = uic.loadUi(ui_file_path, self)

        self.stl_renderer = vtk.vtkRenderer()
        self.ui.vtkWidget.GetRenderWindow().AddRenderer(self.stl_renderer)

        self.stl_interactor = self.ui.vtkWidget.GetRenderWindow().GetInteractor()

        style = vtk.vtkInteractorStyleSwitch()
        style.SetCurrentRenderer(self.stl_renderer)
        style.SetCurrentStyleToTrackballCamera()
        self.stl_interactor.SetInteractorStyle(style)

        self.img_renderer = vtk.vtkRenderer()
        self.ui.Image_SliceViewer.GetRenderWindow().AddRenderer(self.img_renderer)

        self.img_interactor = self.ui.Image_SliceViewer.GetRenderWindow().GetInteractor()
        img_interactor_style = vtk.vtkInteractorStyleImage()

        self.img_interactor.SetInteractorStyle(img_interactor_style)

        self.setup_scene((50, 50, 100))

        self.stl_interactor.Initialize()
        self.img_interactor.Initialize()

    def setup_scene(self, size):
        """set grid scene

        Arguments:
            size {array(3,)} -- size of scene
        """
        colors = vtk.vtkNamedColors()

        self.stl_renderer.SetBackground(colors.GetColor3d("Gray"))

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

        self.stl_renderer.AddActor(axes_actor)
        self.stl_renderer.AddActor(grid_actor)
        self.stl_renderer.ResetCamera()
