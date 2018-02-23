# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtWidgets
import vtk
from uiPythonFile.ui_Versa3dMainWindow import Ui_Versa3dMainWindow
from GUI.MouseInteractorHighLightActor import MouseInteractorHighLightActor

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        
        self.ui = Ui_Versa3dMainWindow()
        self.ui.setupUi(self)
        
        self.StlRenderer = vtk.vtkRenderer()
        self.ui.vtkWidget.GetRenderWindow().AddRenderer(self.StlRenderer)
        self.StlInteractor = self.ui.vtkWidget.GetRenderWindow().GetInteractor()

        style = MouseInteractorHighLightActor()
        style.SetDefaultRenderer(self.StlRenderer)

        self.StlInteractor.SetInteractorStyle(style)
        
        self.ImageRenderer = vtk.vtkRenderer()
        self.ui.slice_viewer.GetRenderWindow().AddRenderer(self.StlRenderer)
        self.ui.ImageInteractor = self.ui.slice_viewer.GetRenderWindow().GetInteractor()

        self.importedObject = []
                
        self.ui.actionImport_STL.triggered.connect(self.import_stl)
        self.ui.SliceButton.clicked.connect(self.slice_stl)
        self.StlInteractor.Initialize()
    
    def import_stl(self):
        
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, 'Open stl' ,"", "stl (*.stl)")
        
        reader = vtk.vtkSTLReader()
        
        reader.SetFileName(fileName[0])
        reader.Update()

        self.importedObject.append(reader.GetOutput())
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        
        self.StlRenderer.AddActor(actor)
        
        self.StlRenderer.ResetCamera()
    
    def slice_stl(self):

        print("start \n")





        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())