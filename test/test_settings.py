import unittest
from PyQt5.QtCore import QSettings, QCoreApplication

from versa3d.settings import Versa3dSettings, PRINTER_CONFIG, PRESET_PARAM_CONFIG
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
        self.singleton.load_all()

    def test_setting_init(self):
        with open(PRINTER_CONFIG) as f:
            printer_default_config = json.load(f)
        
        with open(PRESET_PARAM_CONFIG) as f:
            preset_default_config = json.load(f)

        saved_coord_offset = np.array(
            printer_default_config['bj_printer']['coord_offset']['value'])
        stored_coord_offset = self.singleton.printer['bj_printer'].coord_offset.value
        self.assertTrue(np.all(saved_coord_offset == stored_coord_offset))

        saved_value = preset_default_config['bj_parameter']['layer_thickness']['value']
        stored_value = self.singleton.parameter_preset['bj_parameter'].layer_thickness.value
        self.assertEqual(saved_value, stored_value)

    def test_set_settings(self):
        modified_coord = np.array([10,10], dtype = float)
        self.singleton.clone_printer(0, 'new_printer')
        old_val = self.singleton.printer['new_printer'].coord_offset.value
        self.singleton.printer['new_printer'].coord_offset.value = modified_coord
        self.singleton.save_printer(2)

        singleton_2 = Versa3dSettings()
        singleton_2.load_all()
        new_coord = singleton_2.printer['new_printer'].coord_offset.value

        self.assertTrue(np.all(new_coord == modified_coord))
        self.assertFalse(np.all(new_coord == old_val))

    def tearDown(self):
        settings = QSettings()
        settings.clear()


if __name__ == '__main__':
    unittest.main()
