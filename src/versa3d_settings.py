from PyQt5.QtCore import QSettings


def load_settings(parent):
    settings = QSettings(QSettings.IniFormat,
                         QSettings.UserScope, "MSAM", "Versa3d", parent)

    return settings


def save_settings(parent):

    settings = QSettings(QSettings.IniFormat,
                         QSettings.UserScope, "MSAM", "Versa3d", parent)

    settings.setValue('basic_printer/bed_x', 50.0)
    settings.setValue('basic_printer/bed_y', 50.0)
    settings.setValue('basic_printer/bed_z', 100.0)

    return settings
