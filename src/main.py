# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtWidgets
import vtk
from uiPythonFile.ui_Versa3dMainWindow import Ui_Versa3dMainWindow
from GUI.MouseInteractorHighLightActor import MouseInteractorHighLightActor

from GUI.command import stlImportCommand
from lib.versa3dConfig import config

from collections import deque

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

        self.StlInteractor.Initialize()
    
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
    
    def slice_stl(self):

        print("start \n")



        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())