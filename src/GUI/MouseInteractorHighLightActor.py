

import vtk
from vtk import vtkInteractorStyleTrackballCamera

class MouseInteractorHighLightActor(vtkInteractorStyleTrackballCamera):

    def __init__(self,parent=None):
        self.AddObserver("LeftButtonPressEvent",self.leftButtonPressEvent)

        self.LastPickedActor = None
        self.LastPickedProperty = vtk.vtkProperty()
    
    def leftButtonPressEvent(self,obj,event):
        clickPos = self.GetInteractor().GetEventPosition()
        
        picker = vtk.vtkPropPicker()
        picker.Pick(clickPos[0],clickPos[1], 0 , self.GetDefaultRenderer())

        if(self.LastPickedActor):
            self.LastPickedActor.GetProperty().DeepCopy(self.LastPickedProperty)
        
        self.LastPickedActor = picker.GetActor()

        if(self.LastPickedActor):

            self.LastPickedProperty.DeepCopy(self.LastPickedActor.GetProperty())

            self.LastPickedActor.GetProperty().SetColor(1.0,0,0)
            self.LastPickedActor.GetProperty().SetDiffuse(1.0)
            self.LastPickedActor.GetProperty().SetSpecular(0.0)
        
        self.OnLeftButtonDown()

        return
        




