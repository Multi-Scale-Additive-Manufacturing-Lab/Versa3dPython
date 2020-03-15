# -*- coding: utf-8 -*

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QSettings
from PyQt5 import QtGui
import vtk
from vtk.util import numpy_support
import numpy as np
from designer_files.icon import versa3d_icon
from versa3d.mouse_interaction import ActorHighlight
import versa3d.print_platter as ppl
import versa3d.versa3d_command as vscom
#from versa3d.settings import load_settings, PrinterSettings, PrintheadSettings, PrintSettings


class MainWindow(QtWidgets.QMainWindow):
    """
    main window
    Arguments:
        QtWidgets {QMainWindow} -- main window
    """

    def __init__(self, ui_file_path):
        super().__init__()
        uic.loadUi(ui_file_path, self)

        #self.settings_dict = load_settings()

        self.stl_renderer = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.stl_renderer)

        self.stl_interactor = self.vtkWidget.GetRenderWindow().GetInteractor()

        #Figure out a way to share settings
        self.platter = ppl.PrintPlatter((50,50,100))

        self.platter.signal_add_part.connect(self.render_parts)
        self.platter.signal_add_part.connect(self.add_obj_to_list)

        self.platter.signal_remove_part.connect(self.remove_parts)

        style = vtk.vtkInteractorStyleRubberBand3D()
        self.stl_interactor.SetInteractorStyle(style)

        actor_highlight_obs = ActorHighlight(self)

        style.AddObserver('SelectionChangedEvent', actor_highlight_obs)

        self.setup_scene(self.platter.size)
        self.platter.set_up_dummy_sphere()

        self.stl_interactor.Initialize()

        self.undo_stack = QtWidgets.QUndoStack(self)
        self.undo_stack.setUndoLimit(10)

        self.push_button_x.clicked.connect(self.move_object_x)
        self.push_button_y.clicked.connect(self.move_object_y)

        self.action_undo.triggered.connect(self.undo_stack.undo)
        self.action_redo.triggered.connect(self.undo_stack.redo)

        self.action_import_stl.triggered.connect(self.import_stl)

        #self.initialize_tab()

    def import_stl(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Open stl', "", "stl (*.stl)")
        if(filename[0] != ''):
            com = vscom.ImportCommand(filename[0], self.platter)
            self.undo_stack.push(com)

    def initialize_tab(self):

        tab_names = {'print_settings': "Print Setting",
                     'printhead_settings': "PrintHead",
                     'printer_settings': "Printer"}

        for setting_name, tab_name in tab_names.items():

            page = QtWidgets.QWidget()
            self.MainViewTab.addTab(page, tab_name)

            layout = QtWidgets.QHBoxLayout()
            leftSide = QtWidgets.QVBoxLayout()
            rightSide = QtWidgets.QHBoxLayout()

            stackedWidget = QtWidgets.QStackedWidget()
            rightSide.addWidget(stackedWidget)

            PageSize = page.size()
            RightSideSpacer = QtWidgets.QSpacerItem(PageSize.width()*30/32, 5)
            rightSide.addSpacerItem(RightSideSpacer)

            layout.addLayout(leftSide)
            layout.addLayout(rightSide)

            TopLeftSideLayout = QtWidgets.QHBoxLayout()

            preset_selector = QtWidgets.QComboBox()
            save_button = QtWidgets.QToolButton()
            delete_button = QtWidgets.QToolButton()

            SaveIcon = QtGui.QIcon(":/generic/save.svg")
            save_button.setIcon(SaveIcon)

            DeleteIcon = QtGui.QIcon(":/generic/trash.svg")
            delete_button.setIcon(DeleteIcon)

            TopLeftSideLayout.addWidget(preset_selector)
            TopLeftSideLayout.addWidget(save_button)
            TopLeftSideLayout.addWidget(delete_button)

            leftSide.addLayout(TopLeftSideLayout)

            CategoryList = QtWidgets.QListWidget()

            leftSide.addWidget(CategoryList)

            settings_list = self.settings_dict[setting_name]

            for stored_setting in settings_list:
                preset_selector.addItem(stored_setting.name)

            """
            #CategoryList.itemClicked.connect(self.switchPage)

            pageIndex = 0
            for key, item in self.settings_dict.items():
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
            """
            page.setLayout(layout)

    def populatePage(self, item, page):

        label = item.label
        ValType = item.type
        sidetext = item.sidetext
        default_value = item.default_value

        layout = page.layout()

        sublayout = QtWidgets.QHBoxLayout()

        if(ValType == "Enum"):
            ComboBox = QtWidgets.QComboBox(page)
            enum = item.getEnum()
            for key, val in enum.items():
                ComboBox.addItem(key)

            item.setQObject(ComboBox)
            self.addItem(label, sidetext, [ComboBox], page, sublayout)

        elif(ValType in ["float", "double"]):
            DoubleSpinBox = QtWidgets.QDoubleSpinBox(page)
            self.addItem(label, sidetext, [DoubleSpinBox], page, sublayout)
            DoubleSpinBox.setValue(default_value)
            item.setQObject(DoubleSpinBox)

        elif(ValType == "int"):
            IntSpinBox = QtWidgets.QSpinBox(page)
            self.addItem(label, sidetext, [IntSpinBox], page, sublayout)
            IntSpinBox.setValue(default_value)
            item.setQObject(IntSpinBox)

        elif(ValType == "2dPoint"):
            listOfQtWidget = []
            for i in range(0, 2):
                DoubleSpinBox = QtWidgets.QDoubleSpinBox(page)
                listOfQtWidget.append(DoubleSpinBox)
                DoubleSpinBox.setValue(default_value[i])
                item.addQObject(DoubleSpinBox)

            self.addItem(label, sidetext, listOfQtWidget, page, sublayout)

        layout.addLayout(sublayout)

    def addItem(self, label, sidetext, ListQtWidget, page, layout):
        if(label != ""):
            layout.addWidget(QtWidgets.QLabel(label, page))

        for QtWidget in ListQtWidget:
            layout.addWidget(QtWidget)

        if(sidetext != ""):
            layout.addWidget(QtWidgets.QLabel(sidetext, page))

    @pyqtSlot(QtWidgets.QListWidgetItem)
    def switchPage(self, item):
        category = item.text()
        stackedWidget, index = self.mapPage[category]
        stackedWidget.setCurrentIndex(index)

    # TODO change undo redo, if multiple actor are chosen. Undo and Redo all of them
    def translate(self, delta_pos):
        parts = self.platter.parts
        for part in parts:
            if part.picked:
                com = vscom.TranslationCommand(delta_pos, part.actor)
                self.undo_stack.push(com)

    def move_object_y(self):
        y = self.y_delta.value()
        self.translate(np.array([0, y, 0]))

    def move_object_x(self):
        x = self.x_delta.value()
        self.translate(np.array([x, 0, 0]))

    # TODO implement undo for list
    @pyqtSlot(ppl.PrintObject)
    def add_obj_to_list(self, obj):
        table = self.table_stl
        name = obj.name
        table.insertRow(table.rowCount())

        name_entry = QtWidgets.QTableWidgetItem(name)
        scale_value = QtWidgets.QTableWidgetItem(str(1.0))
        copies_value = QtWidgets.QTableWidgetItem(str(1.0))

        current_row = table.rowCount() - 1
        table.setItem(current_row, 0, name_entry)
        table.setItem(current_row, 1, copies_value)
        table.setItem(current_row, 2, scale_value)

    @pyqtSlot(ppl.PrintObject)
    def render_parts(self, obj):
        self.stl_renderer.AddActor(obj.actor)

    @pyqtSlot(ppl.PrintObject)
    def remove_parts(self, obj):
        self.stl_renderer.RemoveActor(obj.actor)

    def setup_scene(self, size):
        """set grid scene

        Arguments:
            size {array(3,)} -- size of scene
        """
        colors = vtk.vtkNamedColors()

        self.stl_renderer.SetBackground(colors.GetColor3d("lightslategray"))

        # add coordinate axis
        axes_actor = vtk.vtkAxesActor()
        axes_actor.SetShaftTypeToLine()
        axes_actor.SetTipTypeToCone()

        axes_actor.SetTotalLength(*size)

        number_grid = 50

        X = numpy_support.numpy_to_vtk(np.linspace(0, size[0], number_grid))
        Y = numpy_support.numpy_to_vtk(np.linspace(0, size[1], number_grid))
        Z = numpy_support.numpy_to_vtk(np.array([0]*number_grid))

        # set up grid
        grid = vtk.vtkRectilinearGrid()
        grid.SetDimensions(number_grid, number_grid, number_grid)
        grid.SetXCoordinates(X)
        grid.SetYCoordinates(Y)
        grid.SetZCoordinates(Z)

        geometry_filter = vtk.vtkRectilinearGridGeometryFilter()
        geometry_filter.SetInputData(grid)
        geometry_filter.SetExtent(
            0, number_grid - 1, 0, number_grid - 1, 0, number_grid - 1)
        geometry_filter.Update()

        grid_mapper = vtk.vtkPolyDataMapper()
        grid_mapper.SetInputConnection(geometry_filter.GetOutputPort())

        grid_actor = vtk.vtkActor()
        grid_actor.SetMapper(grid_mapper)
        grid_actor.GetProperty().SetRepresentationToWireframe()
        grid_actor.GetProperty().SetColor(colors.GetColor3d('Banana'))
        grid_actor.GetProperty().EdgeVisibilityOn()
        grid_actor.SetPickable(False)
        grid_actor.SetDragable(False)

        self.stl_renderer.AddActor(axes_actor)
        self.stl_renderer.AddActor(grid_actor)
        self.stl_renderer.ResetCamera()
