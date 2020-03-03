# -*- coding: utf-8 -*

from PyQt5 import QtWidgets, uic
import numpy as np
import vtk
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
        self.platter = ppl.print_platter(self.stl_renderer)

        style = vtk.vtkInteractorStyleRubberBand3D()
        self.stl_interactor.SetInteractorStyle(style)

        actor_highlight_obs = actor_highlight(self)

        style.AddObserver('SelectionChangedEvent', actor_highlight_obs)

        x_sc = self.settings.value('basic_printer/bed_x', 50, type=float)
        y_sc = self.settings.value('basic_printer/bed_y', 50, type=float)
        z_sc = self.settings.value('basic_printer/bed_z', 100, type=float)

        self.platter.setup_scene((x_sc, y_sc, z_sc))
        self.platter.set_up_dummy_sphere()

        self.stl_interactor.Initialize()

        self.undo_stack = QtWidgets.QUndoStack(self)
        self.undo_stack.setUndoLimit(10)
