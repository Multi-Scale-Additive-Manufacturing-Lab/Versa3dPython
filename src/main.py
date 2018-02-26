# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtWidgets
import vtk
from GUI.ui_Versa3dMainWindow import Ui_Versa3dMainWindow
from GUI.MouseInteractorHighLightActor import MouseInteractorHighLightActor

from lib.command import stlImportCommand
from lib.versa3dConfig import config , FillEnum

from collections import deque
import numpy as np

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        
        self._config = config('./config/versa3dConfig.ini')

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

        self.undoStack = deque(maxlen=10)
        self.redoStack = deque(maxlen=10)
                
        self.ui.actionImport_STL.triggered.connect(self.import_stl)
        self.ui.SliceButton.clicked.connect(self.slice_stl)
        self.ui.actionUndo.triggered.connect(self.undo)
        self.ui.actionRedo.triggered.connect(self.redo)

        self.setUpScene()

        self.StlInteractor.Initialize()

        self.populateComboBox(FillEnum, self.ui.inFillComboBox)

    
    def import_stl(self):
        importer = stlImportCommand(self.StlRenderer,self)
        importer.execute()

        self.undoStack.append(importer)

    def undo(self):
        if(len(self.undoStack)>0):
            command = self.undoStack.pop()
            command.undo()
            self.redoStack.append(command)

    def redo(self):
        if(len(self.undoStack)>0):
            command = self.redoStack.pop()
            command.redo()
            self.undoStack.append(command)

    def populateComboBox(self,list,combobox):
        combobox.addItems(list)
    
    def setUpScene(self):

        #add coordinate axis
        axesActor = vtk.vtkAxesActor()
        axesActor.SetShaftTypeToLine()
        axesActor.SetTipTypeToCone()
        printBedSize = self._config.getValue('printbedsize')
        buildBedHeight = self._config.getValue('buildheight')
        axesActor.SetTotalLength(printBedSize[0],printBedSize[1],buildBedHeight)

        if(printBedSize[0] <50 or  printBedSize[1] <50):
            Increment = 1.0
        else:
            Increment = 10.0
        
        #create xy plane
        xyPlane = vtk.vtkPlaneSource()
        xyPlane.SetOrigin(0.0,0.0,0.0)
        xyPlane.SetPoint1(printBedSize[0],0,0)
        xyPlane.SetPoint2(0,printBedSize[1],0)
        
        xyPlaneMapper = vtk.vtkPolyDataMapper()
        xyPlaneMapper.SetInputConnection(xyPlane.GetOutputPort())

        xyPlaneActor = vtk.vtkActor()
        xyPlaneActor.SetMapper(xyPlaneMapper)
        xyPlaneActor.SetPickable(False)
        xyPlaneActor.SetDragable(False)
        xyPlaneActor.GetProperty().SetColor(0.2,0.29,0.7)
        
        #create grid
        for i in np.arange(0, printBedSize[0], Increment):
            line = vtk.vtkLineSource()
            line.SetPoint1(i,0,0)
            line.SetPoint2(i,printBedSize[1],0)
            line.Update()

            lineMapper = vtk.vtkPolyDataMapper()
            lineMapper.SetInputConnection(line.GetOutputPort())

            lineActor = vtk.vtkActor()
            lineActor.SetMapper(lineMapper)
            lineActor.SetPickable(False)
            lineActor.SetDragable(False)

            self.StlRenderer.AddActor(lineActor)
        
        for j in np.arange(0, printBedSize[0], Increment):
            line = vtk.vtkLineSource()
            line.SetPoint1(0,j,0)
            line.SetPoint2(printBedSize[0],j,0)
            line.Update()

            lineMapper = vtk.vtkPolyDataMapper()
            lineMapper.SetInputConnection(line.GetOutputPort())

            lineActor = vtk.vtkActor()
            lineActor.SetMapper(lineMapper)
            lineActor.SetPickable(False)
            lineActor.SetDragable(False)

            self.StlRenderer.AddActor(lineActor)

        self.StlRenderer.AddActor(xyPlaneActor)
        self.StlRenderer.AddActor(axesActor)

        self.StlRenderer.ResetCamera()
            
    def slice_stl(self):

        print("start \n")



        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())