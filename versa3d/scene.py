
from vtkmodules import vtkRenderingCore as vtkRC
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor
from vtkmodules.vtkCommonDataModel import vtkRectilinearGrid
from vtkmodules.vtkFiltersGeometry import vtkRectilinearGridGeometryFilter
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkInteractionWidgets import vtkButtonWidget, vtkTexturedButtonRepresentation2D
from vtkmodules.vtkInteractionWidgets import vtkSliderRepresentation2D, vtkSliderWidget
from vtkmodules.vtkIOImage import vtkPNGReader
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject
import numpy as np
from vtkmodules.util import numpy_support
from versa3d.mouse_interaction import RubberBandHighlight
from versa3d.print_platter import PrintObject


class Versa3dScene(QObject):
    selection_start = pyqtSignal()
    selection_end = pyqtSignal()
    selection_pos = pyqtSignal(float, float, float)

    def __init__(self, vtkqwidget: QVTKRenderWindowInteractor) -> None:
        super().__init__(parent=vtkqwidget)

        self._ren = vtkRC.vtkRenderer()
        vtkqwidget.GetRenderWindow().AddRenderer(self._ren)

        self.interactor = vtkqwidget.GetRenderWindow().GetInteractor()
        self.scene_size = [50.0, 50.0, 50.0]
        self._setup_scene(*self.scene_size)

        self.rubber_style = RubberBandHighlight(
            self.selection_cb, self.selection_pos_cb)
        self.interactor.SetInteractorStyle(self.rubber_style)

        self.interactor.GetPickingManager().EnabledOn()
        self.interactor.Initialize()
        self.interactor.Start()

        self._create_button()
        self._create_slider()

        self._ls_obj = {}
        self._ls_sliced_obj = {}

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
        self.button.SetInteractor(self.interactor)
        self.button.SetRepresentation(box_rep)

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

    def selection_pos_cb(self, x: float, y: float, z: float):
        self.selection_pos.emit(x, y, z)

    def selection_cb(self, state: bool):
        if state:
            self.selection_start.emit()
        else:
            self.selection_end.emit()

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
        Z = numpy_support.numpy_to_vtk(np.array([0]*number_grid))

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
        Z = numpy_support.numpy_to_vtk(np.array([0]*number_grid))

        self._grid.SetDimensions(number_grid, number_grid, number_grid)
        self._grid.SetXCoordinates(X)
        self._grid.SetYCoordinates(Y)
        self._grid.SetZCoordinates(Z)

        self._geometry_filter.SetExtent(
            0, number_grid - 1, 0, number_grid - 1, 0, number_grid - 1)
        self._geometry_filter.Update()

        self._ren.GetRenderWindow().Render()

    def _compute_bounds(self, ls_actor) -> np.ndarray:
        bds = np.array([np.inf, -np.inf]*3)
        for obj in ls_actor.values():
            actor = obj.actor
            bounds = np.array(actor.GetBounds())
            min_val = bds[0::2] > bounds[0::2]
            max_val = bds[1::2] < bounds[1::2]

            bds[0::2][min_val] = bounds[0::2][min_val]
            bds[1::2][max_val] = bounds[0::2][max_val]
        return bds

    @pyqtSlot(PrintObject)
    def render(self, obj: PrintObject) -> None:

        if len(self._ls_obj) == 0:
            obj.actor.SetPosition(
                self.scene_size[0]/3.0, self.scene_size[1]/3.0, 0)
        else:
            current_bds = self._compute_bounds(self._ls_obj)
            le = obj.actor.GetLength()
            obj.actor.SetPosition(
                current_bds[1]+le*0.50, current_bds[3]+le*0.50, 0)

        self._ls_obj[obj.id] = obj
        self._ren.AddActor(obj.actor)
        self._ren.GetRenderWindow().Render()

    @pyqtSlot(PrintObject)
    def unrender(self, obj: PrintObject) -> None:
        self._ls_obj.pop(obj.id)
        self._ren.RemoveActor(obj.actor)
        self._ren.GetRenderWindow().Render()

    @pyqtSlot(vtkRC.vtkActor)
    def render_sliced_obj(self, sliced_obj: vtkRC.vtkActor) -> None:
        self._sliced_obj.AddPart(sliced_obj)
        self._ren.GetRenderWindow().Render()
