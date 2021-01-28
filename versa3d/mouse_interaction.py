from vtkmodules.vtkInteractionStyle import vtkInteractorStyleRubberBand3D
from vtkmodules.vtkRenderingCore import vtkCellPicker, vtkAssembly, vtkInteractorStyle, vtkProp3DCollection, vtkRenderedAreaPicker
from vtkmodules.vtkInteractionWidgets import vtkBoxWidget2, vtkBoxRepresentation
from vtkmodules.vtkCommonCore import vtkInformation, vtkInformationVector


class RubberBandHighlight(vtkInteractorStyleRubberBand3D):

    def __init__(self) -> None:
        super().__init__()
        self.selected_actor = []
        self.AddObserver('SelectionChangedEvent', self.highlight)

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

    def highlight(self, obj: vtkInteractorStyleRubberBand3D, event: str) -> None:
        interactor = obj.GetInteractor()
        prop_collection = self.find_poked_actor(obj)
        prop_collection.InitTraversal()
        if prop_collection.GetNumberOfItems() > 0:
            prop = prop_collection.GetNextProp()
            while not prop is None:
                self.selected_actor.append(prop)
                prop.InvokeEvent('StartPickEvent', interactor)
                prop = prop_collection.GetNextProp()
        else:
            for prop in self.selected_actor:
                prop.InvokeEvent('EndPickEvent', interactor)
            self.selected_actor = []

        self.update_render()
