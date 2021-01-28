import numpy as np
from vtkmodules.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtkmodules.vtkInteractionWidgets import vtkBoxWidget
from vtkmodules.vtkCommonCore import vtkInformation, vtkInformationVector
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.util.vtkConstants import VTK_OBJECT
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkRenderingCore import vtkRenderWindowInteractor, vtkActor, vtkRenderer, vtkPolyDataMapper
from vtkmodules.vtkFiltersGeneral import vtkTransformPolyDataFilter
from vtkmodules.util.misc import calldata_type
from PyQt5.QtCore import QUuid

class PrintObject(VTKPythonAlgorithmBase):
    def __init__(self) -> None:
        VTKPythonAlgorithmBase.__init__(
            self, nInputPorts=1, inputType='vtkPolyData', nOutputPorts=1, outputType='vtkPolyData')

        self._actor = vtkActor()
        self._actor.AddObserver('StartPickEvent', self.pick)
        self._actor.AddObserver('EndPickEvent', self.unpick)

        self._box_widget = vtkBoxWidget()
        self._box_widget.TranslationEnabledOn()
        self._box_widget.RotationEnabledOn()
        self._box_widget.ScalingEnabledOff()
        self._box_widget.SetProp3D(self._actor)
        self._box_widget.PickingManagedOn()
        self._box_widget.SetPlaceFactor(1.50)
        self._box_widget.AddObserver('InteractionEvent', self.box_sync)

        self.picked = False
        self._backup_prop = None
        self.id = QUuid.createUuid().toString()
        self.initialised = False

    def box_sync(self, caller : vtkBoxWidget, ev : str) -> None:
        t = vtkTransform()
        caller.GetTransform(t)
        self._actor.SetUserTransform(t)
        self.Modified()

    @property
    def actor(self) -> vtkActor:
        return self._actor

    def render(self, ren: vtkRenderer) -> None:
        ren.AddActor(self._actor)
        ren.GetRenderWindow().Render()
    
    def unrender(self, ren: vtkRenderer) -> None:
        ren.RemoveActor(self._actor)
        ren.GetRenderWindow().Render()

    @calldata_type(VTK_OBJECT)
    def pick(self, caller: vtkActor, ev: str, interactor : vtkRenderWindowInteractor = None) -> None:
        """set pick status

        Args:
            caller (vtkRenderWindowInteractor): object being observed
            ev (string): event type description
        """
        if not interactor is None:
            self._box_widget.SetInteractor(interactor)
            if not self.picked :
                self._box_widget.On()
    
    @calldata_type(VTK_OBJECT)
    def unpick(self, caller: vtkActor, ev: str, interactor : vtkRenderWindowInteractor = None) -> None:
        """set pick status

        Args:
            caller (vtkRenderWindowInteractor): object being observed
            ev (string): event type description
        """
        if not interactor is None:
            self._box_widget.SetInteractor(interactor)
            if not self.picked :
                self._box_widget.Off()

    def move(self, x: float, y: float, z: float) -> None:
        self._actor.AddPosition(x, y, z)
        self.Modified()

    def rotate(self, w: float, x: float, y: float, z: float) -> None:
        self._actor.RotateWXYZ(w, x, y, z)
        self.Modified()

    def RequestData(self, request: str, inInfo: vtkInformation, outInfo: vtkInformation) -> bool:
        input_poly = vtkPolyData.GetData(inInfo[0])

        if not self.initialised:
            mapper = vtkPolyDataMapper()
            mapper.AddInputDataObject(input_poly)
            self._actor.SetMapper(mapper)
            self.initialised = True
        
        self._box_widget.PlaceWidget(self._actor.GetBounds())

        output = vtkPolyData.GetData(outInfo)

        transform = vtkTransform()
        transform.SetMatrix(self._actor.GetMatrix())

        coord_converter = vtkTransformPolyDataFilter()
        coord_converter.SetTransform(transform)
        coord_converter.AddInputData(input_poly)
        coord_converter.Update()
        output.ShallowCopy(coord_converter.GetOutput())

        return 1
