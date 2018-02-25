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
        value = configObject.getValue('Unit')

        self.assertEqual('mm',value)
    
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
        value = configObject.getValue('Unit')
        self.assertEqual('inch', value)

    def tearDown(self):
        os.remove(self.testFileName)
    

if __name__ == '__main__':
    unittest.main()


