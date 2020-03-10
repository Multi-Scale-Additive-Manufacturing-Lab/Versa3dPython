from PyQt5.QtCore import QSettings


def load_settings():
    settings = QSettings()
    return settings


def save_settings(setting, value):
    settings = QSettings()
    settings.setValue(setting, value)
    return settings
