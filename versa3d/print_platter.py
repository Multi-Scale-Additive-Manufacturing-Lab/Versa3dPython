from PyQt5.QtWidgets import QUndoCommand
import numpy as np
from vtkmodules.util.vtkAlgorithm import VTKPythonAlgorithmBase, vtkAlgorithm
from vtkmodules.vtkInteractionWidgets import vtkBoxWidget
from vtkmodules.vtkCommonCore import vtkInformation
from vtkmodules.vtkCommonDataModel import vtkPolyData,vtkDataObject
from vtkmodules.vtkCommonExecutionModel import vtkPolyDataAlgorithm
from vtkmodules.util.vtkConstants import VTK_OBJECT
from vtkmodules.vtkRenderingCore import vtkRenderWindowInteractor, vtkActor, vtkRenderer, vtkPolyDataMapper
from vtkmodules.vtkFiltersGeneral import vtkTransformPolyDataFilter
from vtkmodules.vtkFiltersCore import vtkAppendPolyData
from vtkmodules.vtkFiltersCore import vtkMarchingCubes
from vtkmodules.util.misc import calldata_type
from vtkmodules.util import keys
from vtkmodules.vtkCommonTransforms import vtkTransform
from PyQt5.QtCore import QObject, QUuid, pyqtSlot, pyqtSignal

from typing import Callable, Optional, List
from time import time

from versa3d.slicing import VoxelSlicer
from versa3d.settings import PrintSetting, PixelPrinthead, GenericPrintParameter
import versa3d.versa3d_command as vscom
from enum import IntEnum

ID_KEY = keys.MakeKey(keys.StringKey, 'id', "vtkActor")
TYPE_KEY = keys.MakeKey(keys.IntegerKey, "type", "vtkActor")

class ActorTypeKey(IntEnum):
    Input = 1
    Result = 2

class PrintObject(QObject):
    modified_sig = pyqtSignal(str)

    def __init__(self, poly_src : vtkPolyDataAlgorithm, parent: Optional['QObject'] = None) -> None:
        super().__init__(parent=parent)
        self._poly_src = poly_src
        self.id = QUuid.createUuid().toString()
        self.actor = vtkActor()

        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(poly_src.GetOutputPort())
        self.actor.SetMapper(mapper)

        user_transform = vtkTransform()
        user_transform.Identity()
        user_transform.PostMultiply()
        self.actor.SetUserTransform(user_transform)

        transform = vtkTransform()
        transform.SetMatrix(self.actor.GetMatrix())

        self._coord_converter = vtkTransformPolyDataFilter()
        self._coord_converter.SetTransform(transform)
        self._coord_converter.AddInputData(poly_src.GetOutput())
        self._coord_converter.Update()

        self._voxelizer = VoxelSlicer()
        self._voxelizer.SetInputConnection(self._coord_converter.GetOutputPort())

        self.results = vtkActor()
        self._init_input_id_key()
        self._init_output_id_key(self.results)
    
    def push_transform(self, trs : vtkTransform) -> None:
        user_trs = self.actor.GetUserTransform()
        user_trs.Concatenate(trs)

        self._coord_converter.SetTransform(user_trs)
        self.modified_sig.emit(self.id)
    
    def pop_transform(self) -> None:
        user_trs = self.actor.GetUserTransform()
        user_trs.Pop()

        self._coord_converter.SetTransform(user_trs)
        self.modified_sig.emit(self.id)
    
    def _init_input_id_key(self):
        info = vtkInformation()
        info.Set(ID_KEY, self.id)
        info.Set(TYPE_KEY, ActorTypeKey.Input)
        self.actor.SetPropertyKeys(info)
    
    def _init_output_id_key(self, obj : vtkActor) -> None:
        info = vtkInformation()
        info.Set(ID_KEY, self.id)
        info.Set(TYPE_KEY, ActorTypeKey.Result)

        obj.SetPropertyKeys(info)

    def slice_obj(self, printer: PrintSetting,
                     printhead: PixelPrinthead,
                     print_param: GenericPrintParameter) -> None:

        self._voxelizer.set_settings(printer, printhead, print_param)
        self._voxelizer.Update()

        surf = vtkMarchingCubes()
        surf.SetValue(0, 255)
        surf.AddInputData(self._voxelizer.GetOutputDataObject(0))
        surf.Update()

        polymap = vtkPolyDataMapper()
        polymap.SetInputData(surf.GetOutput())
        
        actor = vtkActor()
        actor.SetMapper(polymap)
        self._init_output_id_key(actor)
        self.results.ShallowCopy(actor)

def arrange_part(ls_part : List[PrintObject], target_obj : PrintObject):
    part_bbox = np.zeros(6)
    ls_bds = np.zeros((len(ls_part), 6))
    for i, obj in enumerate(ls_part):
        bds = np.array(obj.actor.GetBounds())
        ls_bds[i,...] = bds
    
    part_bbox[0::2] = np.min(ls_bds, axis = 0)[0::2]
    part_bbox[1::2] = np.max(ls_bds, axis = 0)[1::2]

    target_obj.actor.SetPosition(part_bbox[1]*1.5, part_bbox[3]*1.5, 0)

class PrintPlatter(QObject):
    render_signal = pyqtSignal(PrintObject)
    unrender_signal = pyqtSignal(PrintObject)
    render_sl_signal = pyqtSignal(PrintObject)
    unrender_sl_signal = pyqtSignal(PrintObject)

    command_sig = pyqtSignal(QUndoCommand)

    def __init__(self, parent: Optional['QObject'] = None) -> None:
        super().__init__(parent=parent)
        self._plate = {}
        self.scene_size = [50.0, 50.0, 50.0]

    def import_part(self, obj_src : vtkPolyDataAlgorithm):
        obj = PrintObject(obj_src)
        obj.modified_sig.connect(self.unrender_sl)
        self.place_object(obj)
        com = vscom.ImportCommand(obj, self)
        self.command_sig.emit(com)
    
    def place_object(self, obj : PrintObject):
        if len(self._plate) == 0:
            obj.actor.SetPosition(
                self.scene_size[0]/3.0, self.scene_size[1]/3.0, 0)
        else:
            arrange_part(self._plate.values(), obj)
    
    def add_part(self, obj : PrintObject):
        self._plate[obj.id] = obj
        self.render_signal.emit(obj)
    
    def remove_part(self, obj : PrintObject):
        self._plate.pop(obj.id)
        self.unrender_signal.emit(obj)
    
    @pyqtSlot(float, float, float)
    def resize_scene(self, x: float, y: float, z: float) -> None:
        self.scene_size[0] = x
        self.scene_size[1] = y
        self.scene_size[2] = z
    
    @pyqtSlot(str)
    def render_sl(self, id : str):
        self.render_sl_signal.emit(self._plate[id])
    
    @pyqtSlot(str)
    def unrender_sl(self, id: str):
        self.unrender_sl_signal.emit(self._plate[id])
    
    @pyqtSlot(list, vtkTransform)
    def apply_transform(self, idx : List[str], trs: vtkTransform):
        ls_obj = [self._plate[id] for id in idx]
        com = vscom.TransformCommand(trs, ls_obj)
        self.command_sig.emit(com)
