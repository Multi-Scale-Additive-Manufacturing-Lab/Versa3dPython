import vtk
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QSettings
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase

class PrintPlatterSource(VTKPythonAlgorithmBase):

    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self,
            nInputPorts=0,
            nOutputPorts=1, outputType='vtkPolyData')

        self.merge_filter = vtk.vtkAppendPolyData()
        self.merge_filter.UserManagedInputsOff()
        self.print_objects = {}
    
    def add_part(self, id, obj):
        self.print_objects[id] = obj
        self.merge_filter.AddInputConnection(0, obj.poly_src.GetOutputPort())
        self.Modified()
        return id
    
    def remove_part(self, id):
        rm_obj = self.print_objects.pop(id)
        self.merge_filter.RemoveInputConnection(0, rm_obj.poly_src.GetOutputPort())
        self.Modified()
        return rm_obj

    def reset_picked(self):
        for _, obj in self.print_objects.items():
            obj.unpick()
    
    def RequestData(self, request, inInfo, outInfo):
        info = outInfo.GetInformationObject(0)
        output = vtk.vtkPolyData.GetData(info)
        self.merge_filter.Update()
        output.ShallowCopy(self.merge_filter.GetOutput())
        return 1

class PrintObject():
    def __init__(self, name, obj_src):
        """object to be printed

        Args:
            name (string): object name
            vtk_obj (vtkPolyDataAlgorithm): object source
        """
        super().__init__()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(obj_src.GetOutputPort())
        self.actor = vtk.vtkActor()
        self.actor.SetMapper(mapper)
        self.poly_src = self.convert_to_polydata(self.actor, obj_src)

        self.picked = False
        self._backup_prop = None
        self.name = name
        self.actor.AddObserver('PickEvent', self.pick)
    
    @staticmethod
    def convert_to_polydata(actor, poly_src):
        clean = vtk.vtkCleanPolyData()

        transform = vtk.vtkTransform()
        transform.SetMatrix(actor.GetMatrix())

        coord_converter = vtk.vtkTransformPolyDataFilter()
        coord_converter.SetTransform(transform)
        coord_converter.SetInputConnection(poly_src.GetOutputPort())
        coord_converter.Update()
        return coord_converter

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
