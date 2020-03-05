import vtk


class actor_highlight:
    def __init__(self, parent):
        super().__init__()

        self.parent = parent

    def __call__(self, caller, ev):
        """[summary]

        Arguments:
            caller {vtkRenderWindowInteractor} -- object being observed
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
                actor.Pick()

    def reset_picked_actors(self):
        self.parent.platter.reset_picked()
