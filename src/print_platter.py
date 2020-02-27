import vtk

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
