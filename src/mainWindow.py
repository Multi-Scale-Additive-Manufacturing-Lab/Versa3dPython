# -*- coding: utf-8 -*

from PyQt5 import QtWidgets, uic
import vtk


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

        self.stl_interactor.Initialize()
        self.img_interactor.Initialize()
