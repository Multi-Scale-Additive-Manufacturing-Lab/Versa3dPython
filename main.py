# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtWidgets
import vtk
from uiPythonFile.ui_Versa3dMainWindow import Ui_Versa3dMainWindow

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        
        self.ui = Ui_Versa3dMainWindow()
        self.ui.setupUi(self)
        
        self.ren = vtk.vtkRenderer()
        self.ui.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.Iren = self.ui.vtkWidget.GetRenderWindow().GetInteractor()
        
        self.ui.actionImport_STL.triggered.connect(self.import_stl)
        self.ui.SliceButton.clicked.connect(self.slice_stl)
        self.Iren.Initialize()
    
    def import_stl(self):
        
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, 'Open stl' ,"", "stl (*.stl)")
        
        reader = vtk.vtkSTLReader()
        
        reader.SetFileName(fileName[0])
        reader.Update()
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        
        self.ren.AddActor(actor)
        
        self.ren.ResetCamera()
    
    def slice_stl(self):

        print("start \n")

        

        
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())