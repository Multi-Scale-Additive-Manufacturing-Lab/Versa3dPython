from vtkmodules.vtkInteractionStyle import vtkInteractorStyleRubberBand3D
from vtkmodules.vtkRenderingCore import vtkCellPicker, vtkAssembly, vtkInteractorStyle, vtkProp3DCollection
from vtkmodules.vtkRenderingCore import vtkRenderedAreaPicker, vtkAssemblyPath, vtkActor, vtkRenderer
from vtkmodules.vtkInteractionWidgets import vtkBoxWidget2, vtkBoxRepresentation
from vtkmodules.vtkCommonCore import vtkInformation, vtkInformationVector
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkCommonMath import vtkMatrix4x4

import numpy as np
from typing import Tuple, Callable

from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject
from PyQt5.QtWidgets import QUndoCommand

from versa3d.print_platter import ID_KEY

class RubberBandHighlight(vtkInteractorStyleRubberBand3D):
    def __init__(self, cb_int : Callable[[bool], None], cb_pos : Callable[[float, float, float], None], cb_com : Callable[[str, vtkTransform], None]) -> None:
        super().__init__()
        self.AddObserver('SelectionChangedEvent', self.highlight)
        self.widget = vtkBoxWidget2()
        self.widget.AddObserver('InteractionEvent', self.move_cb)
        self._selected_actor = None
        self._prev_trs = []

        self._poked_ren = None
        self._platter = None

        self.cb_int = cb_int
        self.cb_pos = cb_pos
        self.cb_com = cb_com

        self._moved = False

    def move_cb(self, caller: vtkBoxWidget2, ev: str) -> None:
        trs = vtkTransform()
        box_rep = caller.GetRepresentation()
        box_rep.GetTransform(trs)
        bds = box_rep.GetBounds()
        self.cb_pos(bds[0], bds[2], bds[4])
        self.apply_transform(trs)

        self._moved = True

    def apply_transform(self, trs : vtkTransform):
        self._selected_actor.InitTraversal()
        obj = self._selected_actor.GetNextProp()
        count = 0
        while not obj is None:
            prev_trs = vtkTransform()
            prev_trs.DeepCopy(self._prev_trs[count])
            prev_trs.Concatenate(trs)

            obj.SetUserTransform(prev_trs)
            obj = self._selected_actor.GetNextProp()
            count += 1

    def commit_transform(self, ls_obj : vtkProp3DCollection):
        ls_obj.InitTraversal()
        obj = ls_obj.GetNextProp()
        idx = []

        trs = vtkTransform()
        box_rep = self.widget.GetRepresentation()
        box_rep.GetTransform(trs)
        count = 0

        while not obj is None:
            old_trs = self._prev_trs[count]
            old_trs.Push()
            obj.SetUserTransform(old_trs)
            info = obj.GetPropertyKeys()
            id = info.Get(ID_KEY)
            idx.append(id)
            obj = ls_obj.GetNextProp()
            count += 1
        
        self.cb_com(idx, trs)

    def find_poked_actor(self, style: vtkInteractorStyleRubberBand3D):
        interactor = style.GetInteractor()

        picker = vtkRenderedAreaPicker()
        start_pos = style.GetStartPosition()
        end_pos = style.GetEndPosition()
        ren = interactor.FindPokedRenderer(start_pos[0], start_pos[1])
        picker.AreaPick(start_pos[0], start_pos[1],
                        end_pos[0], end_pos[1], ren)
        props = picker.GetProp3Ds()
        return props

    def find_poked_renderer(self, style: vtkInteractorStyleRubberBand3D) -> vtkRenderer:
        interactor = style.GetInteractor()
        x = interactor.GetEventPosition()[0]
        y = interactor.GetEventPosition()[1]
        ren = interactor.FindPokedRenderer(x, y)
        return ren
    
    def update_ren(self):
        if not self._poked_ren is None:
            self._poked_ren.GetRenderWindow().Render()
    
    def set_position(self, x, y, z):
        self._moved = True
        box_rep = self.widget.GetRepresentation()
        trs = vtkTransform()
        box_rep.GetTransform(trs)
        bds = box_rep.GetBounds()
        trs.Translate(x - bds[0], y - bds[2], z - bds[4])
        box_rep.SetTransform(trs)
        self.apply_transform(trs)
        self.update_ren()
    
    def compute_bds(self, props : vtkProp3DCollection):
        props.InitTraversal()
        obj = props.GetNextProp()
        n_item = props.GetNumberOfItems()
        bd_boxes = np.zeros((n_item, 6))
        final_bds = np.zeros(6)
        for i in range(n_item):
            bounds = obj.GetBounds()
            obj = props.GetNextProp()
            bd_boxes[i,...] = bounds

        final_bds[0::2] = np.min(bd_boxes, axis = 0)[0::2]
        final_bds[1::2] = np.max(bd_boxes, axis = 0)[1::2]
        return final_bds
    
    def get_user_trs(self, props: vtkProp3DCollection):
        props.InitTraversal()
        obj = props.GetNextProp()
        prev_trs = []
        while not obj is None:
           trs = obj.GetUserTransform()
           if trs is None:
               trs = vtkTransform()
               trs.Identity()
               trs.PostMultiply()
           prev_trs.append(trs)
           obj = props.GetNextProp()
        
        return prev_trs

    def highlight(self, obj: vtkInteractorStyleRubberBand3D, event: str) -> None:
        interactor = obj.GetInteractor()
        self.widget.SetInteractor(interactor)
        props = self.find_poked_actor(obj)
        ren = self.find_poked_renderer(obj)
        self._poked_ren = ren
        
        if props.GetNumberOfItems() > 0:
            box_rep = vtkBoxRepresentation()
            box_rep.SetPlaceFactor(1)
            bds = self.compute_bds(props)
            self._selected_actor = props
            self._prev_trs = self.get_user_trs(props)
            box_rep.PlaceWidget(bds)
            self.widget.SetRepresentation(box_rep)
            self.widget.SetEnabled(1)
            self.cb_int(True)
            self.cb_pos(bds[0], bds[2], bds[4])
        else:
            if not self._selected_actor is None:
                if self._moved:
                    self.commit_transform(self._selected_actor)
                self.widget.SetRepresentation(None)
                self.widget.SetEnabled(0)
                self._selected_actor = None
                self._prev_trs = []
                self._moved = False

            self.cb_int(False)
        self.update_ren()
