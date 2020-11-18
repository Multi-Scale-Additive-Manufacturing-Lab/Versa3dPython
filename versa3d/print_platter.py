import vtk
import numpy as np
from vtk.numpy_interface import dataset_adapter as dsa
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtk.util import keys
from PyQt5.QtCore import QUuid

class PrintObject(VTKPythonAlgorithmBase):
    def __init__(self, poly_src):
        VTKPythonAlgorithmBase.__init__(self,
            nInputPorts=0,
            nOutputPorts=1, outputType='vtkPolyData')
        self._poly_src = poly_src
        self._mapper = vtk.vtkPolyDataMapper()
        self._mapper.SetInputConnection(self._poly_src.GetOutputPort())
        self.actor = vtk.vtkActor()
        self.actor.SetMapper(self._mapper)

        self.picked = False
        self._backup_prop = None
        self.id = QUuid.createUuid().toString()
        self.actor.AddObserver('PickEvent', self.pick)

        self._saturation = None
        self._infill = None
    
    @property
    def saturation(self):
        return self._saturation
    
    @saturation.setter
    def saturation(self, val):
        if val != self._saturation:
            self._saturation = val
            self.Modified()

    @property
    def infill(self):
        return self._infill
    
    @infill.setter
    def infill(self, val):
        if val != self.infill:
            self._infill = val
            self.Modified()

    @staticmethod
    def saturation_key():
        return keys.MakeKey(keys.DoubleKey, "saturation", "PrintObject")
    
    @staticmethod
    def infill_key():
        return keys.MakeKey(keys.StringKey, "infill", "PrintObject")

    def pick(self, caller, ev):
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
            self.actor.ApplyProperties()

            self.picked = True

    def unpick(self):
        if(self.picked and (self._backup_prop is not None)):
            self.actor.GetProperty().DeepCopy(self._backup_prop)
            self.actor.ApplyProperties()

        self.picked = False
    
    def RequestInformation(self, request, inInfo, outInfo):
        outInfo.GetInformationObject(0).Set(
            self.saturation_key(),
            self._saturation)
        
        outInfo.GetInformationObject(0).Set(
            self.infill_key(),
            self._infill
        )
        
        return 1

    def RequestData(self, request, inInfo, outInfo):
        output = vtk.vtkPolyData.GetData(outInfo)

        transform = vtk.vtkTransform()
        transform.SetMatrix(self.actor.GetMatrix())

        coord_converter = vtk.vtkTransformPolyDataFilter()
        coord_converter.SetTransform(transform)
        coord_converter.SetInputConnection(self._poly_src.GetOutputPort())
        coord_converter.Update()
        output.ShallowCopy(coord_converter.GetOutput())

        return 1