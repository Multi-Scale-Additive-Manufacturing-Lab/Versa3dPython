__author__ = "Marc Wang"
__copyright__ = "Copyright (c) 2021 Marc Wang"
__license__ = "BSD-3-Clause"
__maintainer__ = "Marc Wang"
__email__ = "marc.wang@uwaterloo.ca"


from vtkmodules import vtkRenderingCore as vtkRC
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor
from vtkmodules.vtkCommonDataModel import vtkRectilinearGrid
from vtkmodules.vtkFiltersGeometry import vtkRectilinearGridGeometryFilter
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkInteractionWidgets import vtkButtonWidget, vtkTexturedButtonRepresentation2D
from vtkmodules.vtkInteractionWidgets import vtkSliderRepresentation2D, vtkSliderWidget
from vtkmodules.vtkIOImage import vtkPNGReader
from vtkmodules.vtkCommonTransforms import vtkTransform

from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject
import numpy as np
from typing import List
from vtkmodules.util import numpy_support
from versa3d.mouse_interaction import RubberBandHighlight
from versa3d.print_platter import PrintObject, TYPE_KEY, ActorTypeKey


class Versa3dScene(QObject):
    selection_start = pyqtSignal()
    selection_end = pyqtSignal()
    selection_pos = pyqtSignal(float, float, float)

    transform_sig = pyqtSignal(list, vtkTransform)

    def __init__(self, vtkqwidget: QVTKRenderWindowInteractor) -> None:
        super().__init__(parent=vtkqwidget)

        self._ren = vtkRC.vtkRenderer()
        vtkqwidget.GetRenderWindow().AddRenderer(self._ren)

        self.interactor = vtkqwidget.GetRenderWindow().GetInteractor()
        self.scene_size = [50.0, 50.0, 50.0]
        self._setup_scene(*self.scene_size)

        self.rubber_style = RubberBandHighlight(
            self.selection_cb, self.selection_pos_cb, self.transform_cb)
        self.interactor.SetInteractorStyle(self.rubber_style)

        self.interactor.GetPickingManager().EnabledOn()
        self.interactor.Initialize()
        self.interactor.Start()

        self._create_button()
        self._create_slider()

    def _create_button(self):
        im_r_1 = vtkPNGReader()
        im_r_1.SetFileName('./designer_files/icon/vtk_icon/layers-f.png')
        im_r_1.Update()

        im_r_2 = vtkPNGReader()
        im_r_2.SetFileName('./designer_files/icon/vtk_icon/layers.png')
        im_r_2.Update()

        self.button = vtkButtonWidget()
        box_rep = vtkTexturedButtonRepresentation2D()
        box_rep.SetRenderer(self._ren)
        box_rep.SetNumberOfStates(2)
        box_rep.SetButtonTexture(0, im_r_1.GetOutput())
        box_rep.SetButtonTexture(1, im_r_2.GetOutput())
        box_rep.SetState(0)
        self.button.SetInteractor(self.interactor)
        self.button.SetRepresentation(box_rep)
        self.button.AddObserver('StateChangedEvent', self._hide_show_obj)

        coord = vtkRC.vtkCoordinate()
        coord.SetCoordinateSystemToNormalizedDisplay()
        coord.SetValue(1.0, 1.0)

        bds = np.zeros(6)
        sz = 50.0
        bds[0] = coord.GetComputedDisplayValue(self._ren)[0] - sz
        bds[1] = bds[0] + sz
        bds[2] = coord.GetComputedDisplayValue(self._ren)[1] - sz
        bds[3] = bds[2] + sz

        box_rep.SetPlaceFactor(1.0)
        box_rep.PlaceWidget(bds)
        self.button.On()

    def _create_slider(self):
        slider_rep = vtkSliderRepresentation2D()
        slider_rep.SetMinimumValue(0)
        slider_rep.SetMaximumValue(100)
        slider_rep.SetValue(100)

        pt_1 = slider_rep.GetPoint1Coordinate()
        pt_1.SetCoordinateSystemToNormalizedDisplay()
        pt_1.SetViewport(self._ren)
        pt_1.SetValue(0.9, 0.2)

        pt_2 = slider_rep.GetPoint2Coordinate()
        pt_2.SetCoordinateSystemToNormalizedDisplay()
        pt_2.SetViewport(self._ren)
        pt_2.SetValue(0.9, 0.8)

        slider_rep.SetSliderLength(0.075)
        slider_rep.SetSliderWidth(0.05)
        slider_rep.SetEndCapLength(0.05)

        self.slider = vtkSliderWidget()
        self.slider.SetInteractor(self.interactor)
        self.slider.SetRepresentation(slider_rep)
        self.slider.SetAnimationModeToAnimate()
        self.slider.EnabledOn()

    def _hide_show_obj(self, obj: vtkButtonWidget, event: str):
        rep = obj.GetRepresentation()
        vis_state = rep.GetState()

        ls_actor = self._ren.GetActors()
        ls_actor.InitTraversal()

        act = ls_actor.GetNextActor()
        while not act is None:
            info = act.GetPropertyKeys()
            if not info is None:
                t_k = info.Get(TYPE_KEY)
                if ActorTypeKey.Input == t_k:
                    act.SetVisibility(not vis_state)
                elif ActorTypeKey.Result == t_k:
                    act.SetVisibility(vis_state)

            act = ls_actor.GetNextActor()

        self._ren.GetRenderWindow().Render()

    def selection_pos_cb(self, x: float, y: float, z: float):
        self.selection_pos.emit(x, y, z)

    def selection_cb(self, state: bool):
        if state:
            self.selection_start.emit()
        else:
            self.selection_end.emit()

    def transform_cb(self, idx: List[str], trs: vtkTransform) -> None:
        self.transform_sig.emit(idx, trs)

    def _setup_scene(self, x: float, y: float, z: float) -> None:
        colors = vtkNamedColors()

        self._ren.SetBackground(colors.GetColor3d("lightslategray"))

        # add coordinate axis
        self.axes_actor = vtkAxesActor()
        self.axes_actor.SetShaftTypeToLine()
        self.axes_actor.SetTipTypeToCone()
        self.axes_actor.SetPickable(False)
        self.axes_actor.SetDragable(False)

        self.axes_actor.SetTotalLength(x, y, z)

        number_grid = 50

        X = numpy_support.numpy_to_vtk(np.linspace(0, x, number_grid))
        Y = numpy_support.numpy_to_vtk(np.linspace(0, y, number_grid))
        Z = numpy_support.numpy_to_vtk(np.array([0] * number_grid))

        # set up grid
        self._grid = vtkRectilinearGrid()
        self._grid.SetDimensions(number_grid, number_grid, number_grid)
        self._grid.SetXCoordinates(X)
        self._grid.SetYCoordinates(Y)
        self._grid.SetZCoordinates(Z)

        self._geometry_filter = vtkRectilinearGridGeometryFilter()
        self._geometry_filter.SetInputData(self._grid)
        self._geometry_filter.SetExtent(
            0, number_grid - 1, 0, number_grid - 1, 0, number_grid - 1)
        self._geometry_filter.Update()

        grid_mapper = vtkRC.vtkPolyDataMapper()
        grid_mapper.SetInputConnection(self._geometry_filter.GetOutputPort())

        grid_actor = vtkRC.vtkActor()
        grid_actor.SetMapper(grid_mapper)
        grid_actor.GetProperty().SetRepresentationToWireframe()
        grid_actor.GetProperty().SetColor(colors.GetColor3d('Banana'))
        grid_actor.GetProperty().EdgeVisibilityOn()
        grid_actor.SetPickable(False)
        grid_actor.SetDragable(False)

        self._ren.AddActor(self.axes_actor)
        self._ren.AddActor(grid_actor)

        camera = vtkRC.vtkCamera()
        camera.SetPosition([x, y, z])
        camera.SetFocalPoint(0, 0, 0)
        camera.Roll(-110)
        self._ren.SetActiveCamera(camera)

    @pyqtSlot(float, float, float)
    def resize_scene(self, x: float, y: float, z: float) -> None:
        self.scene_size[0] = x
        self.scene_size[1] = y
        self.scene_size[2] = z

        self.axes_actor.SetTotalLength(x, y, z)

        number_grid = 50

        X = numpy_support.numpy_to_vtk(np.linspace(0, x, number_grid))
        Y = numpy_support.numpy_to_vtk(np.linspace(0, y, number_grid))
        Z = numpy_support.numpy_to_vtk(np.array([0] * number_grid))

        self._grid.SetDimensions(number_grid, number_grid, number_grid)
        self._grid.SetXCoordinates(X)
        self._grid.SetYCoordinates(Y)
        self._grid.SetZCoordinates(Z)

        self._geometry_filter.SetExtent(
            0, number_grid - 1, 0, number_grid - 1, 0, number_grid - 1)
        self._geometry_filter.Update()

        self._ren.GetRenderWindow().Render()

    @pyqtSlot(PrintObject)
    def render(self, obj: PrintObject) -> None:
        self._ren.AddActor(obj.actor)
        self._ren.GetRenderWindow().Render()

    @pyqtSlot(PrintObject)
    def unrender(self, obj: PrintObject) -> None:
        self._ren.RemoveActor(obj.actor)
        self._ren.GetRenderWindow().Render()

    @pyqtSlot(PrintObject)
    def render_sliced_obj(self, obj: PrintObject) -> None:
        obj.results.SetPickable(False)
        obj.results.VisibilityOff()
        self._ren.AddActor(obj.results)
        self._ren.GetRenderWindow().Render()

    @pyqtSlot(PrintObject)
    def unrender_sliced_obj(self, obj: PrintObject) -> None:
        self._ren.RemoveActor(obj.results)
        self._ren.GetRenderWindow().Render()
