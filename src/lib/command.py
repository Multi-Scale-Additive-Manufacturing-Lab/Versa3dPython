

import vtk
from PyQt5 import QtWidgets
from src.lib.versa3dConfig import config

class stlImportCommand():

    def __init__(self,renderer,config,parentWidget = None):

        self._renderer = renderer
        self._config = config 
        self._parentWidget = parentWidget

    def execute(self):
        fileName = QtWidgets.QFileDialog.getOpenFileName(self._parentWidget, 'Open stl' ,"", "stl (*.stl)")
        if(fileName[0] != ''):
            reader = vtk.vtkSTLReader()
            reader.SetFileName(fileName[0])
            reader.Update()

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(reader.GetOutputPort())

            self._actor = vtk.vtkActor()
            self._actor.SetMapper(mapper)

            printBedSize = self._config.getMachineSetting('printbedsize')
            zRange = self._actor.GetZRange()

            newPosition = [0]*3

            oldPosition = self._actor.GetPosition()
            newPosition[0] = printBedSize[0]/2
            newPosition[1] = printBedSize[1]/2

            if(zRange[0]<0):
                newPosition[2] = oldPosition[2]-zRange[0]
            else:
                newPosition[2] = oldPosition[2]
            
            self._actor.SetPosition(newPosition)

            key = self._config.getKey("Type","Actor")
            info = vtk.vtkInformation()
            info.Set(key,"PolyData")
            self._actor.GetProperty().SetInformation(info)

            self._renderer.AddActor(self._actor)
            self._renderer.ResetCamera()

            return self._actor
        else:
            return None
        
    def undo(self):
        self._renderer.RemoveActor(self._actor)
    
    def redo(self):
        self._renderer.AddActor(self._actor)
        self._renderer.ResetCamera()

    