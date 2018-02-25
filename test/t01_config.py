import unittest
from src.lib.versa3dConfig import config
from pathlib import Path
import os

class TestConfig(unittest.TestCase):

    def setUp(self):
        self.testFileName = 'test.ini'

    def test_ConfigCreation(self):
        configObject = config(self.testFileName)

        IniFile = Path(self.testFileName)
        #check if file created
        self.assertEqual(True, IniFile.is_file())
    
    def test_ConfigGetValue(self):
        configObject = config(self.testFileName)
        UnitValue = configObject.getValue('Unit')
        self.assertEqual('mm',UnitValue)

        printBedValue = configObject.getValue('PrintBedSize')
        self.assertEqual([10,10], printBedValue)

        FillValue = configObject.getValue('Fill')
        self.assertEqual('Black', FillValue)

        NullValue = configObject.getValue('')
        self.assertEqual('',NullValue)

    
    def test_ModifyConfig(self):
        configObject = config(self.testFileName)
        configObject.setValue('Unit', 'inch')

        value = configObject.getValue('Unit')

        self.assertEqual('inch', value)

    def test_SaveConfig(self):
        configObject = config(self.testFileName)
        configObject.setValue('Unit', 'inch')

        configObject.saveConfig()

        configObject2 = config(self.testFileName)
        value = configObject2.getValue('Unit')
        self.assertEqual('inch', value)

    def tearDown(self):
        os.remove(self.testFileName)
    

if __name__ == '__main__':
    unittest.main()


