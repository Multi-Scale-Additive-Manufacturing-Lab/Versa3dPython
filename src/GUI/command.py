

import vtk
from PyQt5 import QtWidgets

class stlImportCommand():

    def __init__(self,renderer,parentWidget = None):

        self._renderer = renderer 
        self._parentWidget = parentWidget

    def execute(self):
        fileName = QtWidgets.QFileDialog.getOpenFileName(self._parentWidget, 'Open stl' ,"", "stl (*.stl)")

        reader = vtk.vtkSTLReader()
        reader.SetFileName(fileName[0])
        reader.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        self._actor = vtk.vtkActor()
        self._actor.SetMapper(mapper)

        self._renderer.AddActor(self._actor)
        self._renderer.ResetCamera()

    def undo(self):
        self._renderer.RemoveActor(self._actor)
    
    def redo(self):
        self._renderer.AddActor(self._actor)
        self._renderer.ResetCamera()

    