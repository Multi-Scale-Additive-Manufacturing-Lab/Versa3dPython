import vtk


class actor_highlight:
    def __init__(self, parent):
        super().__init__()

        self.parent = parent

        self.picked_actors = []
        self.backup_props = []

    def __call__(self, caller, ev):
        """[summary]

        Arguments:
            interactor {vtkRenderWindowInteractor} -- object being observed
            ev {string} -- event type description
        """

        if isinstance(caller, vtk.vtkInteractorStyleRubberBand3D):
            colors = vtk.vtkNamedColors()

            start_pos = caller.GetStartPosition()
            end_pos = caller.GetEndPosition()

            renderer = self.parent.stl_renderer

            picker = vtk.vtkRenderedAreaPicker()

            picker.AreaPick(start_pos[0], start_pos[1],
                            end_pos[0], end_pos[1], renderer)

            list_actors = picker.GetProp3Ds()
            num_picked_actor = list_actors.GetNumberOfItems()
            
            self.reset_picked_actors()

            for i in range(num_picked_actor):
                actor = list_actors.GetItemAsObject(i)
                actor_property = actor.GetProperty()

                backup_pop = vtk.vtkProperty()
                backup_pop.DeepCopy(actor_property)

                self.backup_props.append(backup_pop)

                actor_property.SetColor(colors.GetColor3d('Red'))
                actor_property.SetDiffuse(1.0)
                actor_property.SetSpecular(0.0)

                self.picked_actors.append(actor)

    def reset_picked_actors(self):

        for actor, a_prop in zip(self.picked_actors, self.backup_props):
            actor.GetProperty().DeepCopy(a_prop)

        self.picked_actors = []
        self.backup_props = []
