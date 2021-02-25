from vtkmodules.vtkInteractionStyle import vtkInteractorStyleRubberBand3D
from vtkmodules.vtkRenderingCore import vtkCellPicker, vtkAssembly, vtkInteractorStyle, vtkProp3DCollection
from vtkmodules.vtkRenderingCore import vtkRenderedAreaPicker, vtkAssemblyPath, vtkActor, vtkRenderer
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
    interaction_start = pyqtSignal(np.ndarray, vtkProp3DCollection)
    interaction_end = pyqtSignal()
    object_position = pyqtSignal(float, float, float)

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
        self._poked_ren = None

    def move_cb(self, caller: vtkBoxWidget2, ev: str) -> None:
        trs = vtkTransform()
        box_rep = caller.GetRepresentation()
        box_rep.GetTransform(trs)

        bds = box_rep.GetBounds()
        self.emitter.object_position.emit(bds[0], bds[2], bds[4])

        self.selected_actor.SetUserTransform(trs)

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

    def find_poked_renderer(self, style: vtkInteractorStyleRubberBand3D) -> vtkRenderer:
        interactor = style.GetInteractor()
        x = interactor.GetEventPosition()[0]
        y = interactor.GetEventPosition()[1]
        ren = interactor.FindPokedRenderer(x, y)
        return ren
    
    def update_ren(self):
        if not self._poked_ren is None:
            self._poked_ren.GetRenderWindow().Render()

    def add_actor_to_assem(self, prop_ls: vtkProp3DCollection, ren: vtkRenderer) -> None:
        prop_ls.InitTraversal()
        prop = prop_ls.GetNextProp()
        while not prop is None:
            self.selected_actor.AddPart(prop)
            ren.RemoveActor(prop)
            prop = prop_ls.GetNextProp()

    def remove_actor_from_assem(self, ren: vtkRenderer) -> None:
        self.selected_actor.InitPathTraversal()
        path = self.selected_actor.GetNextPath()
        while not path is None:
            node = path.GetLastNode()
            mat = node.GetMatrix()
            prop = node.GetViewProp()
            prop.PokeMatrix(mat)
            prop.ComputeMatrix()
            ren.AddActor(prop)
            
            path = self.selected_actor.GetNextPath()
    
    def set_position(self, x, y, z):
        bds = np.array(self.selected_actor.GetBounds())
        diff = np.array([x,y,z]) - bds[0::2]
        self.selected_actor.AddPosition(diff)
        n_bds = self.selected_actor.GetBounds()
        box_rep = self.widget.GetRepresentation()
        box_rep.PlaceWidget(n_bds)
        self.update_ren()

    def highlight(self, obj: vtkInteractorStyleRubberBand3D, event: str) -> None:
        interactor = obj.GetInteractor()
        self.widget.SetInteractor(interactor)
        props = self.find_poked_actor(obj)
        ren = self.find_poked_renderer(obj)
        self._poked_ren = ren
        if props.GetNumberOfItems() > 0:
            self.selected_actor = vtkAssembly()
            ren.AddActor(self.selected_actor)
            box_rep = vtkBoxRepresentation()
            box_rep.SetPlaceFactor(1)
            self.add_actor_to_assem(props, ren)
            bds = np.array(self.selected_actor.GetBounds())
            box_rep.PlaceWidget(bds)
            self.widget.SetRepresentation(box_rep)
            self.widget.SetEnabled(1)

            self.emitter.interaction_start.emit(bds, props)
            self.emitter.object_position.emit(bds[0], bds[2], bds[4])
        else:
            if not self.selected_actor is None:
                ren.RemoveActor(self.selected_actor)
                self.remove_actor_from_assem(ren)
                self.widget.SetRepresentation(None)
                self.widget.SetEnabled(0)
                self.selected_actor = None
            self.emitter.interaction_end.emit()

        self.update_ren()
