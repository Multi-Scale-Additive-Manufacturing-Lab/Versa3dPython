import vtk


class actor_highlight:
    def __init__(self, parent):
        super().__init__()

        self.parent = parent

        self.last_picked_actor = None
        self.last_picked_prop = vtk.vtkProperty()

    def __call__(self, interactor, ev):
        """[summary]
        
        Arguments:
            interactor {vtkRenderWindowInteractor} -- object being observed
            ev {string} -- event type description
        """
        colors = vtk.vtkNamedColors()
        style = interactor.GetInteractorStyle()

        renderer = style.GetCurrentRenderer()

        click_pos = interactor.GetEventPosition()
        picker = vtk.vtkPropPicker()
        picker.Pick(click_pos[0], click_pos[1], 0, renderer)

        # If we picked something before, reset its property
        if self.last_picked_actor:
            self.last_picked_actor.GetProperty().DeepCopy(self.last_picked_prop)

        new_picked_actor = picker.GetActor()

        if new_picked_actor:
            # Save the property of the picked actor so that we can
            # restore it next time
            self.last_picked_prop.DeepCopy(new_picked_actor.GetProperty())
            # Highlight the picked actor by changing its properties
            new_picked_actor.GetProperty().SetColor(colors.GetColor3d('Red'))
            new_picked_actor.GetProperty().SetDiffuse(1.0)
            new_picked_actor.GetProperty().SetSpecular(0.0)

            # save the last picked actor
            self.last_picked_actor = new_picked_actor
            style.SetCurrentStyleToTrackballActor()
        else:
            style.SetCurrentStyleToTrackballCamera()

class actor_movement():
    def __init__(self,parent):
        super().__init__()
        self.parent = parent

    def __call__(self, interactor, ev):
        print('moved actor')
