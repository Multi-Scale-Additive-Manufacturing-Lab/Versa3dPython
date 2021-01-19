import vtk
from PyQt5.QtWidgets import QUndoCommand

from versa3d.controller import Versa3dController


class ActorHighlight(QUndoCommand):
    def __init__(self, renderer: vtk.vtkRenderer, ppl: Versa3dController, parent: QUndoCommand = None) -> None:
        """ highlight interactor observer. Called when SelectionChangedEvent
        is emitted by vtkInteractorStyleRubberBand3D

        Args:
            renderer (vtkRenderer) : renderer
            ppl (PrintPlatterSource) : print platter
            parent (QUndoCommand): parent class
        """
        super().__init__(parent)

        self.renderer = renderer
        self.platter = ppl
        self.list_picked = []

    def __call__(self, caller : vtk.vtkRenderWindowInteractor, ev : str) -> None:
        """ event callback

        Args:
            caller (vtkRenderWindowInteractor): object being observed
            ev (string): event type description
        """

        if isinstance(caller, vtk.vtkInteractorStyleRubberBand3D):

            start_pos = caller.GetStartPosition()
            end_pos = caller.GetEndPosition()

            picker = vtk.vtkRenderedAreaPicker()

            picker.AreaPick(start_pos[0], start_pos[1],
                            end_pos[0], end_pos[1], self.renderer)

            list_actors = picker.GetProp3Ds()
            num_picked_actor = list_actors.GetNumberOfItems()

            self.undo()

            for i in range(num_picked_actor):
                actor = list_actors.GetItemAsObject(i)
                actor.Pick()
                self.list_picked.append(actor)

            self.renderer.GetRenderWindow().Render()

    def redo(self) -> None:
        for actor in self.list_picked:
            actor.Pick()

    def undo(self) -> None:
        self.platter.reset_picked()


class ActorMovement(QUndoCommand):
    def __init__(self, renderer: vtk.vtkRenderer, ppl: Versa3dController, parent: QUndoCommand = None) -> None:
        pass

    def __call__(self, caller : vtk.vtkRenderWindowInteractor, ev : str) -> None:
        pass