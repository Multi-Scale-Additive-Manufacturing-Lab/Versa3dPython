import unittest
from PyQt5.QtCore import QSettings, QCoreApplication

from versa3d.settings import Versa3dSettings, DEFAULT_CONFIG
import json
import numpy as np


class SettingsTest(unittest.TestCase):

    def setUp(self):
        QCoreApplication.setOrganizationName("msam")
        QCoreApplication.setOrganizationDomain("dummy_domain.com")
        QCoreApplication.setApplicationName('test_versa3d')
        self.singleton = Versa3dSettings()

    def test_setting_init(self):
        self.assertTrue(self.singleton.initialized)
        with open(DEFAULT_CONFIG) as f:
            default_config = json.load(f)

        saved_coord_offset = np.array(
            default_config['printer']['coord_offset']['value'])
        self.assertTrue(np.all(saved_coord_offset ==
                               self.singleton.printer.coord_offset))

        saved_value = default_config['parameter_preset']['layer_thickness']['value']
        self.assertEqual(
            saved_value, self.singleton.parameter_preset.layer_thickness)

    def test_set_settings(self):
        test_array = np.array([100.0, 100.0])
        modified_printer_name = 'modified_printer_10'
        self.singleton.clone_setting('printer', modified_printer_name)
        self.singleton.change_printer(modified_printer_name)
        self.assertEqual(self.singleton.printer_name, modified_printer_name)

        self.singleton.update_printer_value('coord_offset', test_array)
        self.singleton.save_to_disk()

        singleton_2 = Versa3dSettings()
        default_val = singleton_2.printer.coord_offset
        self.assertFalse(
            np.all(default_val == test_array)
        )
        singleton_2.change_printer(modified_printer_name)
        changed_val = singleton_2.printer.coord_offset
        self.assertTrue(
            np.all(changed_val == test_array)
        )

    def tearDown(self):
        settings = QSettings()
        settings.clear()


if __name__ == '__main__':
    unittest.main()
