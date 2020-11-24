from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon

class SettingsWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        left_side = QtWidgets.QVBoxLayout()
        right_side = QtWidgets.QVBoxLayout()

        menu_widget = QtWidgets.QListWidget()

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

        left_side.addLayout(top_left_side)
        left_side.addWidget(menu_widget)

        stacked_widget = QtWidgets.QStackedWidget()

        bottom_right_size = QtWidgets.QHBoxLayout()
        apply_button = QtWidgets.QPushButton('apply')
        cancel_button = QtWidgets.QPushButton('cancel')
        bottom_right_size.addWidget(apply_button)
        bottom_right_size.addWidget(cancel_button)

        right_side.addWidget(stacked_widget)
        right_side.addLayout(bottom_right_size)

        layout = QtWidgets.QHBoxLayout()
        layout.addLayout(left_side)
        layout.addLayout(right_side)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)