from PyQt5.QtWidgets import QWidget
from PyQt5 import QtWidgets
from typing import Optional

class MovementPanel(QWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent=parent)
        grid_layout = QtWidgets.QGridLayout()

        translate_label = QtWidgets.QLabel('Translate')
        rotate_label = QtWidgets.QLabel('Rotate')
        axis_label = QtWidgets.QLabel('Axis')
        angle_label = QtWidgets.QLabel('Angle')
        scale_label = QtWidgets.QLabel('Scale')

        lock_aspect_ratio = QtWidgets.QLabel('Lock aspect ratio')
        x_label = QtWidgets.QLabel('X')
        y_label = QtWidgets.QLabel('Y')
        z_label = QtWidgets.QLabel('Z')

        grid_layout.addWidget(x_label, 0, 1)
        grid_layout.addWidget(y_label, 0, 2)
        grid_layout.addWidget(z_label, 0, 3)

        grid_layout.addWidget(translate_label, 1, 0)
        grid_layout.addWidget(rotate_label, 2, 0)
        ls_translate_spin_box = self._create_entry_row(translate_label, grid_layout, 1)
        ls_rotate_spin_box = self._create_entry_row(angle_label, grid_layout, 3)
        ls_axis_spin_box = self._create_entry_row(axis_label, grid_layout, 4)
        ls_scaling_spin_box = self._create_entry_row(scale_label, grid_layout, 5)

        self.setLayout(grid_layout)
    
    def _create_entry_row(self, label, grid, row):
        ls_spin = []
        grid.addWidget(label, row, 0)
        for i in range(3):
            spin_box = QtWidgets.QDoubleSpinBox()
            grid.addWidget(spin_box, row, i+1)
            ls_spin.append(spin_box)
        return ls_spin