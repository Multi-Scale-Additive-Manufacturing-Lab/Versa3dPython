import vtk
from PyQt5.QtWidgets import QUndoCommand


class ActorHighlight(QUndoCommand):
    def __init__(self, parent):
        """ highlight interactor observer. Called when SelectionChangedEvent
        is emitted by vtkInteractorStyleRubberBand3D

        Args:
            parent (QMainWindow): parent class
        """
        super().__init__()

        self.parent = parent
        self.list_picked = []

    def __call__(self, caller, ev):
        """ event callback

        Args:
            caller (vtkRenderWindowInteractor): object being observed
            ev (string): event type description
        """

        if isinstance(caller, vtk.vtkInteractorStyleRubberBand3D):

            start_pos = caller.GetStartPosition()
            end_pos = caller.GetEndPosition()

            renderer = self.parent.stl_renderer

            picker = vtk.vtkRenderedAreaPicker()

            picker.AreaPick(start_pos[0], start_pos[1],
                            end_pos[0], end_pos[1], renderer)

            list_actors = picker.GetProp3Ds()
            num_picked_actor = list_actors.GetNumberOfItems()

            self.undo()

            for i in range(num_picked_actor):
                actor = list_actors.GetItemAsObject(i)
                actor.Pick()
                self.list_picked.append(actor)

            renderer.GetRenderWindow().Render()
    
    def redo(self):
        for actor in self.list_picked:
            actor.Pick()
    
    def undo(self):
        self.parent.platter.reset_picked()