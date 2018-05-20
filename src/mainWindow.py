# -*- coding: utf-8 -*-


from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import PyQt5.QtCore as QtCore
import vtk

from src.GUI.ui_Versa3dMainWindow import Ui_Versa3dMainWindow
import src.GUI.res_rc

from src.lib.command import stlImportCommand
from src.lib.versa3dConfig import config
import src.lib.slicing as sl
from collections import deque
import numpy as np

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        
        self._config = config('./config')
        self.mapPage = {}

        self.ui = Ui_Versa3dMainWindow()
        self.ui.setupUi(self)
        
        self.StlRenderer = vtk.vtkRenderer()
        self.ui.vtkWidget.GetRenderWindow().AddRenderer(self.StlRenderer)
        self.StlInteractor = self.ui.vtkWidget.GetRenderWindow().GetInteractor()

        style = vtk.vtkInteractorStyleSwitch()
        style.SetCurrentRenderer(self.StlRenderer)
        style.SetCurrentStyleToTrackballCamera()
        self.StlInteractor.SetInteractorStyle(style)

        self.ImageRenderer = vtk.vtkRenderer()
        self.ui.Image_SliceViewer.GetRenderWindow().AddRenderer(self.ImageRenderer)
        self.ImageInteractor = self.ui.Image_SliceViewer.GetRenderWindow().GetInteractor()
        ImageInteractorStyle = vtk.vtkInteractorStyleImage()
        self.ImageInteractor.SetInteractorStyle(ImageInteractorStyle)

        #setting undo Stack size
        self.undoStack = deque(maxlen=10)
        self.redoStack = deque(maxlen=10)

        #connect slot        
        self.ui.actionImport_STL.triggered.connect(self.import_stl)
        self.ui.ExportGCodeButton.clicked.connect(self.slice_stl)
        self.ui.actionUndo.triggered.connect(self.undo)
        self.ui.actionRedo.triggered.connect(self.redo)
        self.ui.actionCamera_Mode.triggered.connect(self.SetCameraMode)
        self.ui.actionSelection_Mode.triggered.connect(self.SetSelectionMode)
        self.ui.NumLayerSlider.valueChanged.connect(self.ChangeSliceDisplayed)
        
        self.setUpScene()
        self._ImageMapper = vtk.vtkImageSliceMapper()

        self.StlInteractor.Initialize()
        self.ImageInteractor.Initialize()

        self.InitSettingTab()

    
    def import_stl(self):
        importer = stlImportCommand(self.StlRenderer,self._config,self)
        importer.execute()
        self.ui.vtkWidget.GetRenderWindow().Render()
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

    def InitSettingTab(self):
        
        mapSettingTabName = {'PrintSettings':"Print Setting",
                               'PrintHeadSettings':"PrintHead",
                               'PrinterSettings':"Printer"}

        for settingName,tabName in mapSettingTabName.items():
            page = QtWidgets.QWidget()
            self.ui.MainViewTab.addTab(page,tabName)

            layout = QtWidgets.QHBoxLayout()
            leftSide = QtWidgets.QVBoxLayout()
            rightSide = QtWidgets.QHBoxLayout()

            stackedWidget = QtWidgets.QStackedWidget()
            rightSide.addWidget(stackedWidget)

            PageSize = page.size()
            RightSideSpacer = QtWidgets.QSpacerItem(PageSize.width()*30/32,5)
            rightSide.addSpacerItem(RightSideSpacer)

            layout.addLayout(leftSide)
            layout.addLayout(rightSide)

            TopLeftSideLayout = QtWidgets.QHBoxLayout()
            
            PresetSelector = QtWidgets.QComboBox()
            SaveButton = QtWidgets.QToolButton()
            DeleteButton = QtWidgets.QToolButton()

            SaveIcon = QtGui.QIcon(":/Icon/save.svg")
            SaveButton.setIcon(SaveIcon)

            DeleteIcon = QtGui.QIcon(":/Icon/trash.svg")
            DeleteButton.setIcon(DeleteIcon)

            TopLeftSideLayout.addWidget(PresetSelector)
            TopLeftSideLayout.addWidget(SaveButton)
            TopLeftSideLayout.addWidget(DeleteButton)

            leftSide.addLayout(TopLeftSideLayout)

            CategoryList = QtWidgets.QListWidget()
            CategoryList.itemClicked.connect(self.switchPage)

            leftSide.addWidget(CategoryList)
            
            setting = self._config.getSettings(settingName)

            pageIndex = 0
            for key, item in setting.getSettingList().items():
                category = item.category

                if(len(CategoryList.findItems(category,QtCore.Qt.MatchFixedString)) == 0 and category != "" ):
                    CategoryList.addItem(category)
                    subPage = QtWidgets.QWidget()
                    self.mapPage[category] = (stackedWidget,pageIndex)
                    pageIndex = pageIndex + 1

                    stackedWidget.addWidget(subPage)
                    subPageLayout = QtWidgets.QVBoxLayout()
                    subPage.setLayout(subPageLayout)
                
                subPage = stackedWidget.widget(self.mapPage[category][1])
                self.populatePage(item,subPage)

            page.setLayout(layout)
    
    def populatePage(self,item,page):

        label = item.label
        ValType = item.type
        sidetext = item.sidetext

        layout = page.layout()

        sublayout = QtWidgets.QHBoxLayout()

        if(ValType == "Enum"):
            ComboBox = QtWidgets.QComboBox(page)
            enum = item.getEnum()
            for key, val in enum.items():
                ComboBox.addItem(val)
            
            self.addItem(label,sidetext,ComboBox,page,sublayout)
        elif(ValType in ["float","double"]):
            DoubleSpinBox = QtWidgets.QDoubleSpinBox(page)
            self.addItem(label,sidetext,DoubleSpinBox,page,sublayout)            
        
        layout.addLayout(sublayout)
    
    def addItem(self,label,sidetext,QtWidget,page,layout):
        if(label != ""):
            layout.addWidget(QtWidgets.QLabel(label,page))
        
        layout.addWidget(QtWidget)

        if(sidetext != ""):
            layout.addWidget(QtWidgets.QLabel(sidetext,page))
    
    @pyqtSlot(QtWidgets.QListWidgetItem)
    def switchPage(self,item):
        category = item.text()
        stackedWidget, index = self.mapPage[category]
        stackedWidget.setCurrentIndex(index)


    def setUpScene(self):

        #add coordinate axis
        axesActor = vtk.vtkAxesActor()
        axesActor.SetShaftTypeToLine()
        axesActor.SetTipTypeToCone()
        
        printBedSize = self._config.getMachineSetting('printbedsize')
        buildBedHeight = self._config.getMachineSetting('buildheight')
        axesActor.SetTotalLength(printBedSize[0],printBedSize[1],buildBedHeight)

        if(printBedSize[0] <50 or  printBedSize[1] <50):
            Increment = 1.0
        else:
            Increment = 10.0
        
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

        self.StlRenderer.AddActor(axesActor)

        self.StlRenderer.ResetCamera()
    
    def SetCameraMode(self):
        style = self.StlInteractor.GetInteractorStyle()
        style.SetCurrentStyleToTrackballCamera()
    
    def SetSelectionMode(self):
        style = self.StlInteractor.GetInteractorStyle()
        style.SetCurrentStyleToTrackballActor()

    @pyqtSlot(int)
    def ChangeSliceDisplayed(self,value):
        self.ui.NumLayerSpinBox.setValue(value)
        self._ImageMapper.SetSliceNumber(value)
        self.ui.Image_SliceViewer.GetRenderWindow().Render()
            
    def slice_stl(self):
        #fillSelection = self.ui.inFillComboBox.currentText()
        slicer = sl.slicerFactory('black',self._config)

        actors = self.StlRenderer.GetActors()
        key = self._config.getKey("Type","Actor")

        for i in range(0,actors.GetNumberOfItems()):
            actor = actors.GetItemAsObject(i)
            actorInfo = actor.GetProperty().GetInformation()
            if(actorInfo.Has(key)):
                slicer.addActor(actor)
        
        buildVox = slicer.slice()
        (xDim,yDim,zDim) = buildVox.GetDimensions()

        self.ui.NumLayerSlider.setMinimum(0)
        self.ui.NumLayerSlider.setMaximum(zDim-1)
        
        self._ImageMapper.SetInputData(buildVox)
        self._ImageMapper.BackgroundOn()
        self._ImageMapper.SetOrientationToZ()
        self._ImageMapper.SetSliceNumber(0)
        
        imageActor = vtk.vtkImageSlice()
        imageActor.SetMapper(self._ImageMapper)

        self.ImageRenderer.AddActor(imageActor)
        self.ImageRenderer.ResetCamera()

        self.ui.NumLayerSlider.setValue(0)
        self.ui.ViewerTab.setCurrentIndex(1)



