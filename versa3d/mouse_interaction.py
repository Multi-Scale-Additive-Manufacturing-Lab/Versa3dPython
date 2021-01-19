import vtk
from PyQt5.QtWidgets import QUndoCommand

from vtkmodules.vtkInteractionStyle import vtkInteractorStyleRubberBand3D
from versa3d.controller import Versa3dController


class RubberBandHighlight(vtkInteractorStyleRubberBand3D):

    def __init__(self) -> None:
        super().__init__()
        self.AddObserver('SelectionChangedEvent', self.highlight)
        self.selected_actor = []

    def highlight(self, obj: vtkInteractorStyleRubberBand3D, event: str):

        if isinstance(obj, vtk.vtkInteractorStyleRubberBand3D):
            self.reset()
            ren = obj.GetCurrentRenderer()
            start_pos = obj.GetStartPosition()
            end_pos = obj.GetEndPosition()

            picker = vtk.vtkRenderedAreaPicker()

            picker.AreaPick(start_pos[0], start_pos[1],
                            end_pos[0], end_pos[1], ren)

            list_actors = picker.GetProp3Ds()
            num_picked_actor = list_actors.GetNumberOfItems()

            for i in range(num_picked_actor):
                actor = list_actors.GetItemAsObject(i)
                actor.Pick()
                self.selected_actor.append(actor)

            ren.GetRenderWindow().Render()

    def reset(self):
        for actor in self.selected_actor:
            actor.InvokeEvent('UnPickEvent')

        self.selected_actor = []
