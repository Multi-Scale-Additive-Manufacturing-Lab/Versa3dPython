from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialogButtonBox, QMainWindow, QAbstractButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSettings, Qt, pyqtSignal, pyqtSlot


class SettingsWindow(QMainWindow):
    apply_setting_signal = pyqtSignal()

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
        self.drop_down_list = QtWidgets.QComboBox()

        new_file.clicked.connect(self.create_new_setting)
        delete_file.clicked.connect(self.delete_setting)

        top_left_side.addWidget(new_file)
        top_left_side.addWidget(save_file)
        top_left_side.addWidget(delete_file)
        top_left_side.addWidget(self.drop_down_list)
        top_left_side.insertSpacing(-1, 20)
        self.versa_settings = self.controller.settings
        ls_settings = getattr(self.versa_settings, self.window_type)

        self.stacked_widget = QtWidgets.QStackedWidget()
        self.drop_down_list.currentIndexChanged.connect(self.stacked_widget.setCurrentIndex)
        for name, setting_dict in ls_settings.items():
            self.drop_down_list.addItem(name)
            widget = self.init_tab(name, setting_dict)
            self.stacked_widget.addWidget(widget)

        layout = QtWidgets.QVBoxLayout()

        layout.addLayout(top_left_side)
        layout.addWidget(self.stacked_widget)

        self.button_dialog = QDialogButtonBox(Qt.Horizontal)
        self.button_dialog.addButton(QDialogButtonBox.Apply)
        self.button_dialog.addButton(QDialogButtonBox.Ok)
        self.button_dialog.addButton(QDialogButtonBox.Cancel)
        self.button_dialog.clicked.connect(self.button_clicked)
        layout.addWidget(self.button_dialog)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
    
    @pyqtSlot()
    def create_new_setting(self):
        new_setting_dialog = QDialogButtonBox(Qt.Horizontal, parent = self)
        new_setting_dialog.addButton(QDialogButtonBox.Ok)
        new_setting_dialog.addButton(QDialogButtonBox.Cancel)

        new_setting_dialog.show()
    
    @pyqtSlot()
    def delete_setting(self):
        name = self.drop_down_list.currentText()
        setting_idx = self.drop_down_list.currentIndex()
        getattr(self.versa_settings, 'remove_%s' % self.window_type)(name)
        self.drop_down_list.removeItem(setting_idx)
        widget = self.stacked_widget.widget(setting_idx)
        self.stacked_widget.removeWidget(widget)

    @pyqtSlot(QAbstractButton)
    def button_clicked(self, button):
        role = self.button_dialog.buttonRole(button)
        if role == QDialogButtonBox.ApplyRole:
            self.apply_setting_signal.emit()
        elif role == QDialogButtonBox.AcceptRole:
            self.apply_setting_signal.emit()
            self.close()
        elif role == QDialogButtonBox.RejectRole:
            self.close()

    def init_tab(self, name, setting_dict):
        layout = QtWidgets.QHBoxLayout()
        menu_widget = QtWidgets.QListWidget()
        layout.addWidget(menu_widget)

        sub_stacked_page = QtWidgets.QStackedWidget()
        menu_widget.currentRowChanged.connect(sub_stacked_page.setCurrentIndex)
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
            self.apply_setting_signal.connect(entry.commit_value)
            sec_frame[cat][sec].layout().addWidget(q_entry)
        
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        return widget
        
