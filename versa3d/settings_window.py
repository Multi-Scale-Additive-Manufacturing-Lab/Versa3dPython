from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialogButtonBox, QMainWindow
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSettings, Qt


class SettingsWindow(QMainWindow):

    def __init__(self, controller, window_type, parent=None):
        super().__init__(parent=parent)
        self.controller = controller
        self.window_type = window_type

        top_left_side = QtWidgets.QHBoxLayout()

        new_file_icon = QIcon('designer_files/icon/plus-rectangle.svg')
        new_file = QtWidgets.QPushButton(new_file_icon, '')
        delete_file_icon = QIcon('designer_files/icon/trash.svg')
        delete_file = QtWidgets.QPushButton(delete_file_icon, '')
        save_file_icon = QIcon('designer_files/icon/save.svg')
        save_file = QtWidgets.QPushButton(save_file_icon, '')
        drop_down_list = QtWidgets.QComboBox()

        top_left_side.addWidget(new_file)
        top_left_side.addWidget(save_file)
        top_left_side.addWidget(delete_file)
        top_left_side.addWidget(drop_down_list)

        ls_settings = self.controller.get_settings(self.window_type)

        stacked_widget = QtWidgets.QStackedWidget()
        for name in ls_settings.keys():
            drop_down_list.addItem(name)
            #widget = self.init_tab(name)

        layout = QtWidgets.QVBoxLayout()

        layout.addLayout(top_left_side)
        layout.addWidget(stacked_widget)

        button_dialog = QDialogButtonBox(Qt.Horizontal)
        button_dialog.addButton(QDialogButtonBox.Apply)

        button_dialog.addButton(QDialogButtonBox.Ok)
        button_dialog.addButton(QDialogButtonBox.Cancel)
        
        layout.addWidget(button_dialog)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def init_tab(self, name):
        param_setting = self.controller.get_settings(self.window_type)
        setting = param_setting[name]
        cls_name = type(setting).__name__
        layout = QtWidgets.QHBoxLayout()
        stacked_page = QtWidgets.QStackedWidget()

        menu_widget = QtWidgets.QListWidget()
        layout.addWidget(menu_widget)

        setting = QSettings()
        key = '%s/%s/%s' % format(UI_PATH, self.window_type, cls_name)
        setting.beginGroup(key)
        ls_category = setting.childGroups()
        for cat in ls_category:
            menu_widget.addItem(cat)
            section_frame = QtWidgets.QWidget()
            setting.beginGroup(cat)
            ls_section = setting.childGroups()
            for sec in ls_section:
                box = QtWidgets.QGroupBox(sec)
                box_layout = QtWidgets.QVBoxLayout()
                ls_param = QtWidgets.childGroups()
                for p in ls_param:
                    line_layout = QtWidgets.QHBoxLayout()
                    label = QtWidgets.QLabel(setting.value("%s/label" % (p)))
                    unit = QtWidgets.QLabel(setting.value("%s/unit" % (p)))
                    p_type = setting.value("%s/type" % (p))

    def create_entry_box(self, entry_type, value):
        if entry_type == 'int':
            widget = QtWidgets.QSpinBox()
            widget.setValue(value)
            return widget
        elif entry_type == 'float' or entry_type == 'double':
            widget = QtWidgets.QDoubleSpinBox()
            widget.setValue(value)
            return widget
        elif entry_type == 'Array<int>':
            widget = QtWidgets.QWidget()
            layout = QtWidgets.QHBoxLayout()

            for i in value:
                s_widget = QtWidgets.QSpinBox()
                s_widget.setValue(i)
                layout.addWidget(s_widget)
            
            widget.setLayout(layout)
            return widget
        
