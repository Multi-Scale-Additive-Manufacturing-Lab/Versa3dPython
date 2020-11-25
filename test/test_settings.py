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
        settings = QSettings()
        settings.clear()

        self.singleton = Versa3dSettings()

    def test_setting_init(self):
        self.assertTrue(self.singleton.initialized)
        with open(DEFAULT_CONFIG) as f:
            default_config = json.load(f)

        default_name = 'binder_jetting_printer'

        saved_coord_offset = np.array(
            default_config['binder_jetting_printer']['coord_offset']['value'])
        self.assertTrue(np.all(saved_coord_offset ==
                               self.singleton.get_printer('default_bj_printer').coord_offset))

        saved_value = default_config['binder_jetting_parameter_preset']['layer_thickness']['value']
        self.assertEqual(
            saved_value, self.singleton.get_preset('defaut_bj_parameter').layer_thickness)

    def test_set_settings(self):
        test_array = np.array([100.0, 100.0])
        default_name = 'default_bj_printer'
        modified_printer_name = 'modified_printer_10'
        self.singleton.clone_printer(default_name, modified_printer_name)
        self.singleton.update_printer_value(modified_printer_name, 'coord_offset', test_array)
        self.singleton.save_to_disk('printer', modified_printer_name)

        singleton_2 = Versa3dSettings()
        default_val = singleton_2.get_printer(default_name).coord_offset
        self.assertFalse(
            np.all(default_val == test_array)
        )
        changed_val = singleton_2.get_printer(modified_printer_name).coord_offset
        self.assertTrue(
            np.all(changed_val == test_array)
        )

    def tearDown(self):
        settings = QSettings()
        settings.clear()


if __name__ == '__main__':
    unittest.main()
