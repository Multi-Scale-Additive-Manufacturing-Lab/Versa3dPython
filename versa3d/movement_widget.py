__author__ = "Marc Wang"
__copyright__ = "Copyright (c) 2021 Marc Wang"
__license__ = "BSD-3-Clause"
__maintainer__ = "Marc Wang"
__email__ = "marc.wang@uwaterloo.ca"


from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5 import QtWidgets


class MovementPanel(QWidget):
    translate_sig = pyqtSignal(float, float, float)
    rotate_sig = pyqtSignal(float, float, float)
    scale_sig = pyqtSignal(float, float, float)

    reset_sig = pyqtSignal(float)

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent=parent)
        grid_layout = QtWidgets.QGridLayout()

        translate_label = QtWidgets.QLabel('Translate')
        angle_label = QtWidgets.QLabel('Rotate')
        scale_label = QtWidgets.QLabel('Scale')

        lock_aspect_ratio = QtWidgets.QLabel('Lock aspect ratio')
        x_label = QtWidgets.QLabel('X')
        y_label = QtWidgets.QLabel('Y')
        z_label = QtWidgets.QLabel('Z')

        grid_layout.addWidget(x_label, 0, 1)
        grid_layout.addWidget(y_label, 0, 2)
        grid_layout.addWidget(z_label, 0, 3)

        grid_layout.addWidget(translate_label, 1, 0)
        self.ls_translate_spin_box = self._create_entry_row(
            translate_label, grid_layout, 1)

        for s in self.ls_translate_spin_box:
            s.editingFinished.connect(self._emit_translate_sig)

        self.ls_rotate_spin_box = self._create_entry_row(
            angle_label, grid_layout, 2)

        for s in self.ls_rotate_spin_box:
            s.editingFinished.connect(self._emit_rotate_sig)

        self.ls_scaling_spin_box = self._create_entry_row(
            scale_label, grid_layout, 3)

        for s in self.ls_scaling_spin_box:
            s.editingFinished.connect(self._emit_rotate_sig)

        grid_layout.setRowStretch(4, 1)

        self.setLayout(grid_layout)

    def reset(self):
        self.reset_sig.emit(0)

    @pyqtSlot(float, float, float)
    def update_current_position(self, x: float, y: float, z: float):
        self.ls_translate_spin_box[0].setValue(x)
        self.ls_translate_spin_box[1].setValue(y)
        self.ls_translate_spin_box[2].setValue(z)

    @pyqtSlot()
    def _emit_translate_sig(self):
        x = self.ls_translate_spin_box[0].value()
        y = self.ls_translate_spin_box[1].value()
        z = self.ls_translate_spin_box[2].value()
        self.translate_sig.emit(x, y, z)

    @pyqtSlot()
    def _emit_rotate_sig(self):
        x = self.ls_rotate_spin_box[0].value()
        y = self.ls_rotate_spin_box[1].value()
        z = self.ls_rotate_spin_box[2].value()
        self.rotate_sig.emit(x, y, z)

    @pyqtSlot()
    def _emit_scaling_sig(self):
        x = self.ls_scaling_spin_box[0].value()
        y = self.ls_scaling_spin_box[1].value()
        z = self.ls_scaling_spin_box[2].value()
        self.scale_sig.emit(x, y, z)

    def _create_entry_row(self, label, grid, row):
        ls_spin = []
        grid.addWidget(label, row, 0)
        for i in range(3):
            spin_box = QtWidgets.QDoubleSpinBox()
            grid.addWidget(spin_box, row, i + 1)
            ls_spin.append(spin_box)
            self.reset_sig.connect(spin_box.setValue)
        return ls_spin
