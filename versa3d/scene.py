
from vtkmodules import vtkRenderingCore as vtkRC
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor
from vtkmodules.vtkCommonDataModel import vtkRectilinearGrid
from vtkmodules.vtkFiltersGeometry import vtkRectilinearGridGeometryFilter
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.vtkCommonColor import vtkNamedColors
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject
import numpy as np
from vtkmodules.util import numpy_support
from versa3d.mouse_interaction import RubberBandHighlight


class Versa3dScene(QObject):
    selection_start = pyqtSignal()
    selection_end = pyqtSignal()
    selection_pos = pyqtSignal(float, float, float)

    def __init__(self, vtkqwidget : QVTKRenderWindowInteractor) -> None:
        super().__init__(parent = vtkqwidget)

        self._ren = vtkRC.vtkRenderer()
        vtkqwidget.GetRenderWindow().AddRenderer(self._ren)

        self.interactor = vtkqwidget.GetRenderWindow().GetInteractor()
        self.scene_size = [50.0, 50.0, 50.0]
        self._setup_scene(*self.scene_size)

        self.rubber_style = RubberBandHighlight(self.selection_cb, self.selection_pos_cb)
        self.interactor.SetInteractorStyle(self.rubber_style)

        self.interactor.GetPickingManager().EnabledOn()
        self.interactor.Initialize()
        self.interactor.Start()

        self._ren_obj = vtkRC.vtkAssembly()

        self._sliced_obj = vtkRC.vtkAssembly()
        self._sliced_obj.SetPickable(False)
        self._sliced_obj.SetDragable(False)
        self._sliced_obj.VisibilityOff()

        self._ren.AddActor(self._ren_obj)
        self._ren.AddActor(self._sliced_obj)
    
    def selection_pos_cb(self, x : float, y : float, z : float):
        self.selection_pos.emit(x, y, z)
    
    def selection_cb(self, state : bool):
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
    
    @pyqtSlot(bool)
    def show_sliced_obj(self, state : bool) -> None:
        if state:
            self._sliced_obj.VisibilityOn()
            self._ren_obj.VisibilityOff()
        else:
            self._sliced_obj.VisibilityOff()
            self._ren_obj.VisibilityOn()
        
        self._ren.GetRenderWindow().Render()
    
    @pyqtSlot(vtkRC.vtkActor)
    def render(self, obj : vtkRC.vtkActor) -> None:
        n_prop = self._ren_obj.GetParts().GetNumberOfItems()
        if n_prop == 0:
            obj.SetPosition(self.scene_size[0]/3.0, self.scene_size[1]/3.0, 0)
        else:
            current_bds = self._ren_obj.GetBounds()
            le = obj.GetLength()
            obj.SetPosition(current_bds[1]+le*0.50, current_bds[3]+le*0.50, 0)

        self._ren_obj.AddPart(obj)
        self._ren.GetRenderWindow().Render()
    
    @pyqtSlot(vtkRC.vtkActor)
    def unrender(self, obj : vtkRC.vtkActor) -> None:
        self._ren_obj.RemovePart(obj)
        self._ren.GetRenderWindow().Render()

    @pyqtSlot(vtkRC.vtkActor)
    def render_sliced_obj(self, sliced_obj : vtkRC.vtkActor) -> None:
        self._sliced_obj.AddPart(sliced_obj)
        self._ren.GetRenderWindow().Render()


