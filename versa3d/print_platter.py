import vtk
import numpy as np
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtkmodules.vtkInteractionWidgets import vtkBoxWidget
from PyQt5.QtCore import QUuid


class PrintObject(VTKPythonAlgorithmBase):
    def __init__(self) -> None:
        VTKPythonAlgorithmBase.__init__(
            self, nInputPorts=1, inputType='vtkPolyData', nOutputPorts=1, outputType='vtkPolyData')

        self._actor = vtk.vtkActor()

        self.picked = False
        self._backup_prop = None
        self.id = QUuid.createUuid().toString()
        #self._actor.AddObserver('PickEvent', self.pick)
        #self._actor.AddObserver('UnPickEvent', self.unpick)
        self.initialised = False

    @property
    def actor(self) -> vtk.vtkActor:
        return self._actor

    def render(self, ren: vtk.vtkRenderer) -> None:
        ren.AddActor(self._actor)
        ren.GetRenderWindow().Render()
    
    def unrender(self, ren: vtk.vtkRenderer) -> None:
        ren.RemoveActor(self._actor)
        ren.GetRenderWindow().Render()

    def pick(self, caller: vtk.vtkRenderWindowInteractor, ev: str) -> None:
        """set pick status

        Args:
            caller (vtkRenderWindowInteractor): object being observed
            ev (string): event type description
        """
        if(not self.picked):
            colors = vtk.vtkNamedColors()
            actor_property = self.actor.GetProperty()
            self._backup_prop = vtk.vtkProperty()
            self._backup_prop.DeepCopy(actor_property)

            actor_property.SetColor(colors.GetColor3d('Red'))
            actor_property.SetDiffuse(1.0)
            actor_property.SetSpecular(0.0)
            self._actor.ApplyProperties()

            self.picked = True
        else:
            self.unpick(caller, ev)

    def unpick(self, caller: vtk.vtkRenderWindowInteractor, ev: str) -> None:
        if(self.picked and (self._backup_prop is not None)):
            self._actor.GetProperty().DeepCopy(self._backup_prop)
            self._actor.ApplyProperties()

        self.picked = False

    def move(self, x: float, y: float, z: float) -> None:
        self._actor.AddPosition(x, y, z)
        self.Modified()

    def rotate(self, w: float, x: float, y: float, z: float) -> None:
        self._actor.RotateWXYZ(w, x, y, z)
        self.Modified()

    def RequestData(self, request: str, inInfo: vtk.vtkInformation, outInfo: vtk.vtkInformation) -> bool:
        input_poly = vtk.vtkPolyData.GetData(inInfo[0])

        if not self.initialised:
            mapper = vtk.vtkPolyDataMapper()
            mapper.AddInputDataObject(input_poly)
            self._actor.SetMapper(mapper)
            self.initialised = True

        output = vtk.vtkPolyData.GetData(outInfo)

        transform = vtk.vtkTransform()
        transform.SetMatrix(self._actor.GetMatrix())

        coord_converter = vtk.vtkTransformPolyDataFilter()
        coord_converter.SetTransform(transform)
        coord_converter.AddInputData(input_poly)
        coord_converter.Update()
        output.ShallowCopy(coord_converter.GetOutput())

        return 1
