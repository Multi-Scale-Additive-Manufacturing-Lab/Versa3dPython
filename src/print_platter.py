import vtk
from vtk.util import numpy_support
import numpy as np


class print_object():
    def __init__(self, vtk_obj):
        super().__init__()
        self._vtkactor = vtk_obj
        self._picked_state = False
        self._backup_prop = None

    @property
    def actor(self):
        return self._vtkactor

    @property
    def picked(self):
        return self._picked_state

    def pick(self, caller, ev):
        if(not self._picked_state):
            colors = vtk.vtkNamedColors()
            actor_property = self._vtkactor.GetProperty()
            self._backup_prop = vtk.vtkProperty()
            self._backup_prop.DeepCopy(actor_property)

            actor_property.SetColor(colors.GetColor3d('Red'))
            actor_property.SetDiffuse(1.0)
            actor_property.SetSpecular(0.0)

            self._picked_state = True

    def unpick(self):
        if(self._picked_state and (self._backup_prop is not None)):
            self._vtkactor.GetProperty().DeepCopy(self._backup_prop)

        self._picked_state = False


class print_platter():

    def __init__(self, renderer):
        super().__init__()

        self._parts = []
        self._renderer = renderer

    @property
    def platter(self):
        return self._parts

    def add_parts(self, part):
        self._parts.append(part)
        self._renderer.AddActor(part.actor)

    def reset_picked(self):
        for part in self._parts:
            if(part.picked):
                part.unpick()

    def set_up_dummy_sphere(self):
        for i in range(5):
            source = vtk.vtkSphereSource()

            # random position and radius
            x = vtk.vtkMath.Random(0, 50)
            y = vtk.vtkMath.Random(0, 50)
            z = vtk.vtkMath.Random(0, 100)
            radius = vtk.vtkMath.Random(.5, 1.0)

            source.SetRadius(radius)
            source.SetCenter(x, y, z)
            source.SetPhiResolution(11)
            source.SetThetaResolution(21)

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(source.GetOutputPort())
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)

            r = vtk.vtkMath.Random(.4, 1.0)
            g = vtk.vtkMath.Random(.4, 1.0)
            b = vtk.vtkMath.Random(.4, 1.0)
            actor.GetProperty().SetDiffuseColor(r, g, b)
            actor.GetProperty().SetDiffuse(.8)
            actor.GetProperty().SetSpecular(.5)
            actor.GetProperty().SetSpecularColor(1.0, 1.0, 1.0)
            actor.GetProperty().SetSpecularPower(30.0)

            print_obj = print_object(actor)
            actor.AddObserver('PickEvent', print_obj.pick)
            self.add_parts(print_obj)

    def setup_scene(self, size):
        """set grid scene

        Arguments:
            size {array(3,)} -- size of scene
        """
        colors = vtk.vtkNamedColors()

        self._renderer.SetBackground(colors.GetColor3d("Gray"))

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

        self._renderer.AddActor(axes_actor)
        self._renderer.AddActor(grid_actor)
        self._renderer.ResetCamera()
