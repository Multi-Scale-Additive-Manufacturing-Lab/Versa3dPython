import vtk
from PyQt5.QtWidgets import QUndoCommand

from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch, vtkInteractorStyleTrackballCamera, vtkInteractorStyleTrackballActor
from vtkmodules.vtkRenderingCore import vtkCellPicker, vtkAssembly
from versa3d.controller import Versa3dController
from enum import IntEnum


class RubberBandHighlight(vtkInteractorStyleSwitch):

    def __init__(self) -> None:
        super().__init__()
        self.SetCurrentStyleToTrackballCamera()
        track_ball_cam = self.GetCurrentStyle()
        track_ball_cam.AddObserver('LeftButtonPressEvent', self.highlight)
        #self.AddObserver('LeftButtonPressEvent', move_actor)
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

    def highlight(self, obj: vtkInteractorStyleTrackballCamera, event: str):

        interactor = obj.GetInteractor()
        if not interactor.GetShiftKey():
            self.reset()

        x = interactor.GetEventPosition()[0]
        y = interactor.GetEventPosition()[1]
        picker = vtkCellPicker()
        ren = interactor.FindPokedRenderer(x, y)
        picker.Pick(x, y, 0, ren)

        prop = picker.GetViewProp()
        if not prop is None:
            prop.Pick()
            self.selected_actor.AddPart(prop)

        ren.GetRenderWindow().Render()

        obj.OnLeftButtonDown()
