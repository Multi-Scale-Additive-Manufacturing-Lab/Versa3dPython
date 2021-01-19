import vtk
from PyQt5.QtWidgets import QUndoCommand

from vtkmodules.vtkInteractionStyle import vtkInteractorStyleRubberBand3D
from vtkmodules.vtkRenderingCore import vtkCellPicker, vtkAssembly
from versa3d.controller import Versa3dController
from enum import IntEnum


class RubberBandHighlight(vtkInteractorStyleRubberBand3D):

    def __init__(self) -> None:
        super().__init__()

        self.actor_mode = False

        self.AddObserver('SelectionChangedEvent', highlight)
        self.AddObserver('LeftButtonPressEvent', move_actor)
        self.picker = vtk.vtkRenderedAreaPicker()
        self.selected_actor = vtkAssembly()

    def reset(self):
        actor_it = self.selected_actor.GetParts()
        actor_it.InitTraversal()

        if actor_it.GetNumberOfItems() > 0:
            actor = actor_it.GetNextProp3D()
            while actor:
                actor.InvokeEvent('UnPickEvent')
                actor = actor_it.GetNextProp3D()

            self.selected_actor = vtkAssembly()


def move_actor(obj: RubberBandHighlight, event: str):
    interactor = obj.GetInteractor()
    x = interactor.GetEventPosition()[0]
    y = interactor.GetEventPosition()[1]
    ray_picker = vtkCellPicker()
    ray_picker.SetTolerance(0.001)
    ren = interactor.FindPokedRenderer(x, y)

    ray_picker.Pick(x, y, 0.0, ren)

    picked_actor = ray_picker.GetViewProp()
    if picked_actor != None:
        is_selected = obj.selected_actor.GetParts().IsItemPresent(picked_actor)
        obj.actor_mode = True
    else:
        obj.OnLeftButtonDown()


def highlight(obj: RubberBandHighlight, event: str):
    obj.actor_mode = False
    interactor = obj.GetInteractor()
    if not interactor.GetShiftKey():
        obj.reset()

    start_pos = obj.GetStartPosition()
    end_pos = obj.GetEndPosition()
    ren = interactor.FindPokedRenderer(start_pos[0], start_pos[1])

    obj.picker.AreaPick(start_pos[0], start_pos[1],
                        end_pos[0], end_pos[1], ren)

    list_actors = obj.picker.GetProp3Ds()
    num_picked_actor = list_actors.GetNumberOfItems()

    for i in range(num_picked_actor):
        actor = list_actors.GetItemAsObject(i)
        actor.Pick()
        obj.selected_actor.AddPart(actor)

    ren.GetRenderWindow().Render()
