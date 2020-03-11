from PyQt5 import QtWidgets

class versa3d_single_option():
    def __init__(self):
        super().__init__()
        self._value = None

        self.label = ""
        self.tooltip = ""
        self.sidetext = ""
        self.category = ""
        self.subcategory = ""

        self.default_value = None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val
