import vtk
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QSettings


class PrintObject():
    def __init__(self, name, vtk_obj):
        """object to be printed

        Args:
            name (string): object name
            vtk_obj (vtkactor): vtkactor being rendered
        """
        super().__init__()
        self._vtkactor = vtk_obj
        self._picked_state = False
        self._backup_prop = None
        self._name = name
        self._vtkactor.AddObserver('PickEvent', self.pick)

    @property
    def actor(self):
        return self._vtkactor

    @property
    def name(self):
        return self._name

    @property
    def picked(self):
        return self._picked_state

    def pick(self, caller, ev):
        """set pick status

        Args:
            caller (vtkRenderWindowInteractor): object being observed
            ev (string): event type description
        """
        if(not self._picked_state):
            colors = vtk.vtkNamedColors()
            actor_property = self._vtkactor.GetProperty()
            self._backup_prop = vtk.vtkProperty()
            self._backup_prop.DeepCopy(actor_property)

            actor_property.SetColor(colors.GetColor3d('Red'))
            actor_property.SetDiffuse(1.0)
            actor_property.SetSpecular(0.0)
            self._vtkactor.ApplyProperties()

            self._picked_state = True

    def unpick(self):
        if(self._picked_state and (self._backup_prop is not None)):
            self._vtkactor.GetProperty().DeepCopy(self._backup_prop)
            self._vtkactor.ApplyProperties()

        self._picked_state = False


class PrintPlatter(QObject):
    # Qt signal
    signal_add_part = pyqtSignal(PrintObject)
    signal_remove_part = pyqtSignal(PrintObject)

    def __init__(self, size):
        """Print platter class

        Args:
            size (array(2,)): print bed size
        """        
        QObject.__init__(self)
        self._parts = []
        self._size = size

    @property
    def size(self):
        return self._size

    @property
    def parts(self):
        return self._parts

    def add_parts(self, part):
        """ add part to print platter

        Args:
            part (PrintObject): object to be printed
        """ 
        self._parts.append(part)
        self.signal_add_part.emit(part)

    def remove_part(self, part):
        """Remove object from build plate

        Args:
            part (PrintObject): object to be printed
        """
        self._parts.remove(part)
        self.signal_remove_part.emit(part)

    def reset_picked(self):
        for part in self._parts:
            if(part.picked):
                part.unpick()

    def set_up_dummy_sphere(self):
        """set up dummy sphere for debug
        """
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

            print_obj = PrintObject('Dummy_Sphere_{}'.format(i), actor)
            self.add_parts(print_obj)
