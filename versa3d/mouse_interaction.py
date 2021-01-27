import vtk
from PyQt5.QtWidgets import QUndoCommand

from vtkmodules.vtkInteractionStyle import vtkInteractorStyleRubberBand3D
from vtkmodules.vtkRenderingCore import vtkCellPicker, vtkAssembly, vtkInteractorStyle
from vtkmodules.vtkInteractionWidgets import vtkBoxWidget
from versa3d.controller import Versa3dController
from enum import IntEnum

import numpy as np

class RubberBandHighlight(vtkInteractorStyleRubberBand3D):

    def __init__(self) -> None:
        super().__init__()
        #track_ball_camera.AddObserver('LeftButtonPressEvent', self.highlight)
        #track_ball_camera.AddObserver('LeftButtonPressEvent', self.switch_mode)
        self.selected_actor = vtkAssembly()
        self.AddObserver('SelectionChangedEvent', self.highlight)

        self.box_widget = vtkBoxWidget()
        self.box_widget.TranslationEnabledOn()
        self.box_widget.RotationEnabledOn()
        self.box_widget.ScalingEnabledOff()
        self.box_widget.AddObserver('InteractionEvent', self.box_cb)
        self.box_widget.SetPlaceFactor(1.25)
        self.PickingManagedOn()

    def reset(self) -> None:
        actor_it = self.selected_actor.GetParts()
        if actor_it.GetNumberOfItems() > 0:
            self.selected_actor = vtkAssembly()
            self.box_widget.Off()
    
    def find_poked_actor(self, style : vtkInteractorStyle):
        interactor = style.GetInteractor()

        picker = vtk.vtkRenderedAreaPicker()
        start_pos = style.GetStartPosition()
        end_pos = style.GetEndPosition()
        ren = interactor.FindPokedRenderer(start_pos[0], start_pos[1])
        picker.AreaPick(start_pos[0], start_pos[1],end_pos[0], end_pos[1], ren)
        prop = picker.GetViewProp()
        return prop
    
    def update_render(self):
        interactor = self.GetInteractor()
        x = interactor.GetEventPosition()[0]
        y = interactor.GetEventPosition()[1]
        ren = interactor.FindPokedRenderer(x, y)
        ren.GetRenderWindow().Render()
    
    def highlight(self, obj: vtkInteractorStyleRubberBand3D, event: str) -> None:
        interactor = obj.GetInteractor()
        self.box_widget.SetInteractor(interactor)
        if not interactor.GetShiftKey():
            self.reset()
        prop = self.find_poked_actor(obj)
        if not prop is None:
            self.selected_actor.AddPart(prop)
            self.box_widget.SetProp3D(prop)
            self.box_widget.PlaceWidget(prop.GetBounds())
            self.box_widget.On()
        
        self.update_render()
    
    def box_cb(self, obj : vtkBoxWidget, event : str):
        t = vtk.vtkTransform()
        obj.GetTransform(t)
        obj.GetProp3D().SetUserTransform(t)
        self.update_render()
