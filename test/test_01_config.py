import unittest
from src.lib.versa3dConfig import config
from pathlib import Path
import os

class TestConfig(unittest.TestCase):

    def setUp(self):
        self.testFileName = 'config/test.ini'

    def test_ConfigCreation(self):
        configObject = config(self.testFileName)

        IniFile = Path(self.testFileName)
        #check if file created
        self.assertEqual(True, IniFile.is_file())
    
    def test_ConfigGetValue(self):
        configObject = config(self.testFileName)
        UnitValue = configObject.getValue('unit')
        self.assertEqual('mm',UnitValue)

        printBedValue = configObject.getValue('printbedsize')
        self.assertEqual([10,10], printBedValue)

        FillValue = configObject.getValue('layer_thickness')
        self.assertEqual(0.1, FillValue)

        NullValue = configObject.getValue('')
        self.assertEqual('',NullValue)
 
    def test_ModifyConfig(self):
        configObject = config(self.testFileName)
        configObject.setValue('unit', 'inch')

        value = configObject.getValue('unit')

        self.assertEqual('inch', value)

    def test_SaveConfig(self):
        configObject = config(self.testFileName)
        configObject.setValue('unit', 'inch')

        configObject.saveConfig()
        del configObject

        configObject2 = config(self.testFileName)
        value = configObject2.getValue('unit')
        self.assertEqual('inch', value)

        FillValue = configObject2.getValue('layer_thickness')
        self.assertEqual(0.1, FillValue)

        PrintBedArray = configObject2.getValue('printbedsize')
        self.assertEqual([10,10], PrintBedArray)

    def tearDown(self):
        os.remove(self.testFileName)

def suite():
    suite = unittest.TestSuite()

    suite.addTest(TestConfig)
    return suite




