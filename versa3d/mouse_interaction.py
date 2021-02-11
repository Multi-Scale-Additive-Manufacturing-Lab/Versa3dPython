from vtkmodules.vtkInteractionStyle import vtkInteractorStyleRubberBand3D
from vtkmodules.vtkRenderingCore import vtkCellPicker, vtkAssembly, vtkInteractorStyle, vtkProp3DCollection, vtkRenderedAreaPicker, vtkAssemblyPath, vtkActor
from vtkmodules.vtkInteractionWidgets import vtkBoxWidget2, vtkBoxRepresentation
from vtkmodules.vtkCommonCore import vtkInformation, vtkInformationVector
from vtkmodules.vtkCommonTransforms import vtkTransform

import numpy as np
from typing import Tuple

from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject
from PyQt5.QtWidgets import QUndoCommand

from versa3d.print_platter import ID_KEY

class MouseSignalEmitter(QObject):
    commit_move = pyqtSignal(vtkTransform, vtkTransform, vtkActor, str)

    def __init__(self, parent: QObject = None) -> None:
        super().__init__(parent=parent)

class RubberBandHighlight(vtkInteractorStyleRubberBand3D):
    def __init__(self) -> None:
        super().__init__()
        self.selected_actor = None
        self.AddObserver('SelectionChangedEvent', self.highlight)
        self.widget = vtkBoxWidget2()
        self.widget.AddObserver('InteractionEvent', self.move_cb)

        self.emitter = MouseSignalEmitter()

        self._init_t = []
        self._first = True

    def move_cb(self, caller: vtkBoxWidget2, ev: str) -> None:
        trs = vtkTransform()
        box_rep = caller.GetRepresentation()
        box_rep.GetTransform(trs)
        self.selected_actor.InitTraversal()
        prop = self.selected_actor.GetNextProp()

        c = 0
        local_trigger = False
        while not prop is None:
            p_t = prop.GetUserTransform()
            if p_t is None:
                p_t = vtkTransform()
                p_t.PostMultiply()
                p_t.Identity()
                prop.SetUserTransform(p_t)

            if self._first:
                old_t = vtkTransform()
                old_t.DeepCopy(p_t)
                self._init_t.append(old_t)
                p_t.Concatenate(trs)
                local_trigger = True
            else:
                old_t = self._init_t[c]

                copy_t = vtkTransform()
                copy_t.DeepCopy(old_t)
                copy_t.Concatenate(trs)
                prop.SetUserTransform(copy_t)
            c += 1
            prop = self.selected_actor.GetNextProp()

        if local_trigger:
            self._first = False

    def find_poked_actor(self, style: vtkInteractorStyleRubberBand3D) -> vtkProp3DCollection:
        interactor = style.GetInteractor()

        picker = vtkRenderedAreaPicker()
        start_pos = style.GetStartPosition()
        end_pos = style.GetEndPosition()
        ren = interactor.FindPokedRenderer(start_pos[0], start_pos[1])
        picker.AreaPick(start_pos[0], start_pos[1],
                        end_pos[0], end_pos[1], ren)
        props = picker.GetProp3Ds()
        return props

    def update_render(self) -> None:
        interactor = self.GetInteractor()
        x = interactor.GetEventPosition()[0]
        y = interactor.GetEventPosition()[1]
        ren = interactor.FindPokedRenderer(x, y)
        ren.GetRenderWindow().Render()

    def compute_bound(self, prop_ls: vtkProp3DCollection) -> np.array:
        prop_ls.InitTraversal()
        prop = prop_ls.GetNextProp()

        init_bd = np.array([np.PINF, np.NINF]*3, dtype=float)

        while not prop is None:
            bds = np.array(prop.GetBounds())
            min_b = bds[0::2]
            max_b = bds[1::2]

            min_mask = min_b < init_bd[0::2]
            max_mask = max_b > init_bd[1::2]

            init_bd[0::2][min_mask] = min_b[min_mask]
            init_bd[1::2][max_mask] = max_b[max_mask]
            prop = prop_ls.GetNextProp()

        return init_bd

    def highlight(self, obj: vtkInteractorStyleRubberBand3D, event: str) -> None:
        interactor = obj.GetInteractor()
        self.widget.SetInteractor(interactor)
        props = self.find_poked_actor(obj)

        if props.GetNumberOfItems() > 0:
            box_rep = vtkBoxRepresentation()
            box_rep.SetPlaceFactor(1)
            self.selected_actor = props
            bds = self.compute_bound(props)
            box_rep.PlaceWidget(bds)
            self.widget.SetRepresentation(box_rep)
            self.widget.SetEnabled(1)
        else:
            if not self.selected_actor is None:
                self.selected_actor.InitTraversal()
                prop = self.selected_actor.GetNextProp()

                c = 0
                while not prop is None:
                    p_t = prop.GetUserTransform()
                    o_t = self._init_t[c]
                    actor_property = prop.GetProperty()
                    info = actor_property.GetInformation()
                    id = info.Get(ID_KEY)
                    self.emitter.commit_move.emit(p_t, o_t, prop, id)
                    c += 1
                    prop = self.selected_actor.GetNextProp()

                self._init_t = []
                self._first = True
                self.selected_actor = None
            self.widget.SetRepresentation(None)
            self.widget.SetEnabled(0)
        self.update_render()
