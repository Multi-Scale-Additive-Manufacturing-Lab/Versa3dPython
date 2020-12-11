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
        top_left_side.insertSpacing(-1, 20)

        ls_settings = self.controller.get_settings(self.window_type)

        stacked_widget = QtWidgets.QStackedWidget()
        for name, setting_dict in ls_settings.items():
            drop_down_list.addItem(name)
            widget = self.init_tab(name, setting_dict)
            stacked_widget.addWidget(widget)

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

    def init_tab(self, name, setting_dict):
        layout = QtWidgets.QHBoxLayout()
        menu_widget = QtWidgets.QListWidget()
        layout.addWidget(menu_widget)

        sub_stacked_page = QtWidgets.QStackedWidget()
        layout.addWidget(sub_stacked_page)

        cat_frame = {}
        sec_frame = {}
        for entry in setting_dict.values():
            cat = entry.ui['category']
            if not cat in cat_frame.keys():
                single_frame = QtWidgets.QWidget()
                single_frame.setLayout(QtWidgets.QVBoxLayout())
                cat_frame[cat] = single_frame
                menu_widget.addItem(cat)
                sec_frame[cat] = {}
                sub_stacked_page.addWidget(single_frame)
            
            sec = entry.ui['section']
            if not sec in sec_frame[cat].keys():
                box_layout = QtWidgets.QVBoxLayout()
                qbox = QtWidgets.QGroupBox(sec)
                qbox.setLayout(box_layout)
                sec_frame[cat][sec] = qbox
                cat_frame[cat].layout().addWidget(qbox)
            
            q_entry = entry.create_ui_entry()
            sec_frame[cat][sec].layout().addWidget(q_entry)
        
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        return widget
        
