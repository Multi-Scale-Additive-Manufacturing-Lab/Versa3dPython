
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

    def pick(self):
        if(not self._picked_state):
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
