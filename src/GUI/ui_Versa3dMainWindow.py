# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Versa3dMainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Versa3dMainWindow(object):
    def setupUi(self, Versa3dMainWindow):
        Versa3dMainWindow.setObjectName("Versa3dMainWindow")
        Versa3dMainWindow.resize(1004, 640)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Versa3dMainWindow.sizePolicy().hasHeightForWidth())
        Versa3dMainWindow.setSizePolicy(sizePolicy)
        Versa3dMainWindow.setMinimumSize(QtCore.QSize(1004, 600))
        self.centralWidget = QtWidgets.QWidget(Versa3dMainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.centralWidget)
        self.horizontalLayout_3.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_3.setSpacing(6)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.main_horizontal_layout = QtWidgets.QHBoxLayout()
        self.main_horizontal_layout.setContentsMargins(11, 11, 11, 11)
        self.main_horizontal_layout.setSpacing(6)
        self.main_horizontal_layout.setObjectName("main_horizontal_layout")
        self.ViewerTab = QtWidgets.QTabWidget(self.centralWidget)
        self.ViewerTab.setObjectName("ViewerTab")
        self.Model_ViewerTab = QtWidgets.QWidget()
        self.Model_ViewerTab.setObjectName("Model_ViewerTab")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.Model_ViewerTab)
        self.horizontalLayout_2.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.vtkWidget = QVTKRenderWindowInteractor(self.Model_ViewerTab)
        self.vtkWidget.setMinimumSize(QtCore.QSize(600, 500))
        self.vtkWidget.setObjectName("vtkWidget")
        self.horizontalLayout_2.addWidget(self.vtkWidget)
        self.ViewerTab.addTab(self.Model_ViewerTab, "")
        self.Slice_ViewerTab = QtWidgets.QWidget()
        self.Slice_ViewerTab.setObjectName("Slice_ViewerTab")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.Slice_ViewerTab)
        self.horizontalLayout_6.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_6.setSpacing(6)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.Image_SliceViewer = QVTKRenderWindowInteractor(self.Slice_ViewerTab)
        self.Image_SliceViewer.setObjectName("Image_SliceViewer")
        self.horizontalLayout_6.addWidget(self.Image_SliceViewer)
        self.sliderGroup = QtWidgets.QVBoxLayout()
        self.sliderGroup.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.sliderGroup.setContentsMargins(11, 11, 11, 11)
        self.sliderGroup.setSpacing(6)
        self.sliderGroup.setObjectName("sliderGroup")
        self.NumLayerLabel = QtWidgets.QLabel(self.Slice_ViewerTab)
        self.NumLayerLabel.setMinimumSize(QtCore.QSize(40, 20))
        self.NumLayerLabel.setMaximumSize(QtCore.QSize(60, 16777215))
        self.NumLayerLabel.setObjectName("NumLayerLabel")
        self.sliderGroup.addWidget(self.NumLayerLabel)
        self.NumLayerSpinBox = QtWidgets.QSpinBox(self.Slice_ViewerTab)
        self.NumLayerSpinBox.setMinimumSize(QtCore.QSize(40, 20))
        self.NumLayerSpinBox.setMaximumSize(QtCore.QSize(60, 16777215))
        self.NumLayerSpinBox.setObjectName("NumLayerSpinBox")
        self.sliderGroup.addWidget(self.NumLayerSpinBox)
        self.NumLayerSlider = QtWidgets.QSlider(self.Slice_ViewerTab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.NumLayerSlider.sizePolicy().hasHeightForWidth())
        self.NumLayerSlider.setSizePolicy(sizePolicy)
        self.NumLayerSlider.setMinimumSize(QtCore.QSize(0, 0))
        self.NumLayerSlider.setMaximumSize(QtCore.QSize(60, 16777215))
        self.NumLayerSlider.setOrientation(QtCore.Qt.Vertical)
        self.NumLayerSlider.setObjectName("NumLayerSlider")
        self.sliderGroup.addWidget(self.NumLayerSlider)
        self.horizontalLayout_6.addLayout(self.sliderGroup)
        self.ViewerTab.addTab(self.Slice_ViewerTab, "")
        self.main_horizontal_layout.addWidget(self.ViewerTab)
        self.right_side_vertical_layout = QtWidgets.QVBoxLayout()
        self.right_side_vertical_layout.setContentsMargins(11, 11, 11, 11)
        self.right_side_vertical_layout.setSpacing(6)
        self.right_side_vertical_layout.setObjectName("right_side_vertical_layout")
        self.GenerateMachineCodeButton = QtWidgets.QPushButton(self.centralWidget)
        self.GenerateMachineCodeButton.setObjectName("GenerateMachineCodeButton")
        self.right_side_vertical_layout.addWidget(self.GenerateMachineCodeButton)
        self.SliceButton = QtWidgets.QPushButton(self.centralWidget)
        self.SliceButton.setObjectName("SliceButton")
        self.right_side_vertical_layout.addWidget(self.SliceButton)
        self.splitter_right_side = QtWidgets.QSplitter(self.centralWidget)
        self.splitter_right_side.setOrientation(QtCore.Qt.Vertical)
        self.splitter_right_side.setObjectName("splitter_right_side")
        self.layoutWidget = QtWidgets.QWidget(self.splitter_right_side)
        self.layoutWidget.setObjectName("layoutWidget")
        self.layout_split_right_tab = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.layout_split_right_tab.setContentsMargins(11, 11, 11, 11)
        self.layout_split_right_tab.setSpacing(6)
        self.layout_split_right_tab.setObjectName("layout_split_right_tab")
        self.tabWidget = QtWidgets.QTabWidget(self.layoutWidget)
        self.tabWidget.setMinimumSize(QtCore.QSize(325, 100))
        self.tabWidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.tabWidget.setObjectName("tabWidget")
        self.slice_tab = QtWidgets.QWidget()
        self.slice_tab.setObjectName("slice_tab")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.slice_tab)
        self.horizontalLayout_4.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_4.setSpacing(6)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.tabWidget.addTab(self.slice_tab, "")
        self.infill_tab = QtWidgets.QWidget()
        self.infill_tab.setObjectName("infill_tab")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.infill_tab)
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.inFilltype_label = QtWidgets.QLabel(self.infill_tab)
        self.inFilltype_label.setObjectName("inFilltype_label")
        self.verticalLayout.addWidget(self.inFilltype_label)
        self.inFillComboBox = QtWidgets.QComboBox(self.infill_tab)
        self.inFillComboBox.setObjectName("inFillComboBox")
        self.verticalLayout.addWidget(self.inFillComboBox)
        self.tabWidget.addTab(self.infill_tab, "")
        self.raster_tab = QtWidgets.QWidget()
        self.raster_tab.setObjectName("raster_tab")
        self.tabWidget.addTab(self.raster_tab, "")
        self.layout_split_right_tab.addWidget(self.tabWidget)
        self.optionTabs = QtWidgets.QTabWidget(self.splitter_right_side)
        self.optionTabs.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.optionTabs.setObjectName("optionTabs")
        self.machine_tab = QtWidgets.QWidget()
        self.machine_tab.setObjectName("machine_tab")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.machine_tab)
        self.horizontalLayout.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.systemImage = QtWidgets.QLabel(self.machine_tab)
        self.systemImage.setText("")
        self.systemImage.setObjectName("systemImage")
        self.horizontalLayout.addWidget(self.systemImage)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_4.setSpacing(6)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.machineLabel = QtWidgets.QLabel(self.machine_tab)
        self.machineLabel.setObjectName("machineLabel")
        self.verticalLayout_4.addWidget(self.machineLabel)
        self.processLabel = QtWidgets.QLabel(self.machine_tab)
        self.processLabel.setObjectName("processLabel")
        self.verticalLayout_4.addWidget(self.processLabel)
        self.horizontalLayout.addLayout(self.verticalLayout_4)
        self.optionTabs.addTab(self.machine_tab, "")
        self.machines_settingstab = QtWidgets.QWidget()
        self.machines_settingstab.setObjectName("machines_settingstab")
        self.optionTabs.addTab(self.machines_settingstab, "")
        self.output_tab = QtWidgets.QWidget()
        self.output_tab.setObjectName("output_tab")
        self.optionTabs.addTab(self.output_tab, "")
        self.scripting_tab = QtWidgets.QWidget()
        self.scripting_tab.setObjectName("scripting_tab")
        self.optionTabs.addTab(self.scripting_tab, "")
        self.right_side_vertical_layout.addWidget(self.splitter_right_side)
        self.main_horizontal_layout.addLayout(self.right_side_vertical_layout)
        self.horizontalLayout_3.addLayout(self.main_horizontal_layout)
        Versa3dMainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(Versa3dMainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1004, 22))
        self.menuBar.setObjectName("menuBar")
        self.menuFile = QtWidgets.QMenu(self.menuBar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QtWidgets.QMenu(self.menuBar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuSelection = QtWidgets.QMenu(self.menuBar)
        self.menuSelection.setObjectName("menuSelection")
        Versa3dMainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtWidgets.QToolBar(Versa3dMainWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        Versa3dMainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtWidgets.QStatusBar(Versa3dMainWindow)
        self.statusBar.setObjectName("statusBar")
        Versa3dMainWindow.setStatusBar(self.statusBar)
        self.actionImport_STL = QtWidgets.QAction(Versa3dMainWindow)
        self.actionImport_STL.setObjectName("actionImport_STL")
        self.actionUndo = QtWidgets.QAction(Versa3dMainWindow)
        self.actionUndo.setObjectName("actionUndo")
        self.actionRedo = QtWidgets.QAction(Versa3dMainWindow)
        self.actionRedo.setObjectName("actionRedo")
        self.actioncopy = QtWidgets.QAction(Versa3dMainWindow)
        self.actioncopy.setObjectName("actioncopy")
        self.actionpaste = QtWidgets.QAction(Versa3dMainWindow)
        self.actionpaste.setObjectName("actionpaste")
        self.actiondelete = QtWidgets.QAction(Versa3dMainWindow)
        self.actiondelete.setObjectName("actiondelete")
        self.actionSelection_Mode = QtWidgets.QAction(Versa3dMainWindow)
        self.actionSelection_Mode.setObjectName("actionSelection_Mode")
        self.actionCamera_Mode = QtWidgets.QAction(Versa3dMainWindow)
        self.actionCamera_Mode.setObjectName("actionCamera_Mode")
        self.menuFile.addAction(self.actionImport_STL)
        self.menuEdit.addAction(self.actionUndo)
        self.menuEdit.addAction(self.actionRedo)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actioncopy)
        self.menuEdit.addAction(self.actionpaste)
        self.menuEdit.addAction(self.actiondelete)
        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuEdit.menuAction())
        self.menuBar.addAction(self.menuSelection.menuAction())
        self.mainToolBar.addAction(self.actionSelection_Mode)
        self.mainToolBar.addAction(self.actionCamera_Mode)

        self.retranslateUi(Versa3dMainWindow)
        self.ViewerTab.setCurrentIndex(0)
        self.tabWidget.setCurrentIndex(1)
        self.optionTabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Versa3dMainWindow)
        Versa3dMainWindow.setTabOrder(self.optionTabs, self.GenerateMachineCodeButton)
        Versa3dMainWindow.setTabOrder(self.GenerateMachineCodeButton, self.tabWidget)

    def retranslateUi(self, Versa3dMainWindow):
        _translate = QtCore.QCoreApplication.translate
        Versa3dMainWindow.setWindowTitle(_translate("Versa3dMainWindow", "MainWindow"))
        self.ViewerTab.setTabText(self.ViewerTab.indexOf(self.Model_ViewerTab), _translate("Versa3dMainWindow", "Model Viewer"))
        self.NumLayerLabel.setText(_translate("Versa3dMainWindow", "Layer #"))
        self.ViewerTab.setTabText(self.ViewerTab.indexOf(self.Slice_ViewerTab), _translate("Versa3dMainWindow", "Slice Viewer"))
        self.GenerateMachineCodeButton.setText(_translate("Versa3dMainWindow", "Generate Machine Code"))
        self.SliceButton.setText(_translate("Versa3dMainWindow", "Slice"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.slice_tab), _translate("Versa3dMainWindow", "Slice"))
        self.inFilltype_label.setText(_translate("Versa3dMainWindow", "infill type"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.infill_tab), _translate("Versa3dMainWindow", "Infill"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.raster_tab), _translate("Versa3dMainWindow", "Raster"))
        self.machineLabel.setText(_translate("Versa3dMainWindow", "Machine: MSAM Research Platform"))
        self.processLabel.setText(_translate("Versa3dMainWindow", "Process: Hybrid Silicone AM "))
        self.optionTabs.setTabText(self.optionTabs.indexOf(self.machine_tab), _translate("Versa3dMainWindow", "Machine"))
        self.optionTabs.setTabText(self.optionTabs.indexOf(self.machines_settingstab), _translate("Versa3dMainWindow", "Machine Settings"))
        self.optionTabs.setTabText(self.optionTabs.indexOf(self.output_tab), _translate("Versa3dMainWindow", "Output"))
        self.optionTabs.setTabText(self.optionTabs.indexOf(self.scripting_tab), _translate("Versa3dMainWindow", "Scripting"))
        self.menuFile.setTitle(_translate("Versa3dMainWindow", "File"))
        self.menuEdit.setTitle(_translate("Versa3dMainWindow", "Edit"))
        self.menuSelection.setTitle(_translate("Versa3dMainWindow", "View"))
        self.actionImport_STL.setText(_translate("Versa3dMainWindow", "Import stl"))
        self.actionUndo.setText(_translate("Versa3dMainWindow", "Undo"))
        self.actionRedo.setText(_translate("Versa3dMainWindow", "Redo"))
        self.actioncopy.setText(_translate("Versa3dMainWindow", "cut"))
        self.actionpaste.setText(_translate("Versa3dMainWindow", "copy"))
        self.actiondelete.setText(_translate("Versa3dMainWindow", "paste"))
        self.actionSelection_Mode.setText(_translate("Versa3dMainWindow", "Selection Mode"))
        self.actionCamera_Mode.setText(_translate("Versa3dMainWindow", "Camera Mode"))

from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor