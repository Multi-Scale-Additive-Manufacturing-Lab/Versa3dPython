__author__ = "Marc Wang"
__copyright__ = "Copyright (c) 2021 MSAM Lab - University of Waterloo"
__license__ = "BSD-3-Clause"
__maintainer__ = "Marc Wang"
__email__ = "marc.wang@uwaterloo.ca"


from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialogButtonBox, QDialog, QAbstractButton, QInputDialog, QMessageBox, QComboBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QObject
from versa3d.settings import SingleEntry, PrintSetting, SettingWrapper

import attr

class SettingsWindow(QDialog):
    apply_setting_signal = pyqtSignal()

    def __init__(self, slave_cmb: QComboBox,
                setting_obj : SettingWrapper, 
                parent: QObject = None):
        super().__init__(parent=parent)
        self.setting_obj =setting_obj

        init_idx = slave_cmb.currentIndex()

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
        save_file.clicked.connect(self.save_setting)

        top_left_side.addWidget(new_file)
        top_left_side.addWidget(save_file)
        top_left_side.addWidget(delete_file)
        top_left_side.addWidget(self.drop_down_list)
        top_left_side.insertSpacing(-1, 20)
        ls_settings = setting_obj.setting

        self.stacked_widget = QtWidgets.QStackedWidget()
        self.drop_down_list.currentIndexChanged.connect(
            self.stacked_widget.setCurrentIndex)
        for name, setting_dict in ls_settings.items():
            self.drop_down_list.addItem(name)
            widget = self.init_tab(setting_dict)
            self.stacked_widget.addWidget(widget)
        self.drop_down_list.setCurrentIndex(init_idx)
        self.drop_down_list.currentIndexChanged.connect(
            slave_cmb.setCurrentIndex)
        layout = QtWidgets.QVBoxLayout()

        layout.addLayout(top_left_side)
        layout.addWidget(self.stacked_widget)

        self.button_dialog = QDialogButtonBox(Qt.Horizontal)
        self.button_dialog.addButton(QDialogButtonBox.Apply)
        self.button_dialog.addButton(QDialogButtonBox.Ok)
        self.button_dialog.addButton(QDialogButtonBox.Cancel)
        self.button_dialog.clicked.connect(self.button_clicked)
        layout.addWidget(self.button_dialog)

        self.setLayout(layout)

    @pyqtSlot()
    def create_new_setting(self) -> None:
        new_name, ok = QInputDialog.getText(
            self, 'New Setting', 'Enter new name:')
        idx = self.drop_down_list.currentIndex()
        is_duplicate = self.drop_down_list.findText(new_name) != -1
        if len(new_name) != 0 and ok and not is_duplicate:
            setting_dict = self.setting_obj.clone(idx, new_name)
            self.drop_down_list.addItem(new_name)
            widget = self.init_tab(setting_dict)
            self.stacked_widget.addWidget(widget)
            self.drop_down_list.setCurrentIndex(
                self.drop_down_list.count() - 1)
        elif len(new_name) == 0:
            msg_box = QMessageBox(self)
            msg_box.setText("Empty string, please specify name :")
            msg_box.exec()
        elif is_duplicate:
            msg_box = QMessageBox(self)
            msg_box.setText("Deplicate string, please specify another name :")
            msg_box.exec()

    @pyqtSlot()
    def save_setting(self) -> None:
        setting_idx = self.drop_down_list.currentIndex()
        self.setting_obj.save(setting_idx)

    @pyqtSlot()
    def delete_setting(self) -> None:
        setting_idx = self.drop_down_list.currentIndex()
        self.setting_obj.remove(setting_idx)
        self.drop_down_list.removeItem(setting_idx)
        widget = self.stacked_widget.widget(setting_idx)
        self.stacked_widget.removeWidget(widget)

    @pyqtSlot(QAbstractButton)
    def button_clicked(self, button: QAbstractButton) -> None:
        role = self.button_dialog.buttonRole(button)
        if role == QDialogButtonBox.ApplyRole:
            self.apply_setting_signal.emit()
        elif role == QDialogButtonBox.AcceptRole:
            self.apply_setting_signal.emit()
            self.accept()
        elif role == QDialogButtonBox.RejectRole:
            self.reject()

    def init_tab(self, setting_dict: PrintSetting) -> QtWidgets.QWidget:
        layout = QtWidgets.QHBoxLayout()
        menu_widget = QtWidgets.QListWidget()
        layout.addWidget(menu_widget)

        sub_stacked_page = QtWidgets.QStackedWidget()
        menu_widget.currentRowChanged.connect(sub_stacked_page.setCurrentIndex)
        layout.addWidget(sub_stacked_page)

        cat_frame = {}
        sec_frame = {}
        for entry in attr.asdict(setting_dict, recurse=False).values():
            if isinstance(entry, SingleEntry):
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
