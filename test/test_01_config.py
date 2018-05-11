import unittest
import src.lib.versa3dConfig as vc
from pathlib import Path
import os
import shutil

class TestConfig(unittest.TestCase):

    def setUp(self):
        self.testFileFolder = './configtest'
        os.mkdir(self.testFileFolder)

    def test_ConfigGetValue(self):
        configObject = vc.config(self.testFileFolder)

        versa3dSetting = configObject.getSettings('Versa3dSettings')
        printerSetting = configObject.getSettings('PrinterSettings')
        printheadSetting = configObject.getSettings('PrintHeadSettings')
        SliceSetting = configObject.getSettings('PrintSettings')

        UnitValue = versa3dSetting.getSettingValue('Versa3d','unit')
        self.assertEqual('mm',UnitValue)

        printBedValue = printerSetting.getSettingValue('BMVlasea','printbedsize')
        self.assertEqual([30,30], printBedValue)

        buffersizeLimit = printheadSetting.getSettingValue('Imtech','buffersizelimit')
        self.assertEqual([150,-1], buffersizeLimit)

        FillValue = SliceSetting.getSettingValue('BinderJet','layer_thickness')
        self.assertEqual(0.1, FillValue)

        gantryXYVelocity = printerSetting.getSettingValue('BMVlasea','gantryxyvelocity')
        self.assertEqual([100,100],gantryXYVelocity)

        printBedValue = configObject.getMachineSetting('printbedsize')
        self.assertEqual([30,30], printBedValue)
 
    def test_ModifyConfig(self):
        configObject = vc.config(self.testFileFolder)

        versa3dSetting = configObject.getSettings('Versa3dSettings')

        versa3dSetting.setSettingValue('Versa3d','unit','inch')

        value = versa3dSetting.getSettingValue('Versa3d','unit')

        self.assertEqual('inch', value)
    
    def test_ConfigCreation(self):
        configObject = vc.config(self.testFileFolder)

        configObject.saveAll()
        
        listOfFolder = ["Versa3dSettings", "PrintSettings", "PrinterSettings", "PrintHeadSettings"]
        
        for folder in listOfFolder:
            SettingFolder = os.path.join(self.testFileFolder,folder)
            SettingFile = Path(os.path.join(SettingFolder,"Default.ini"))
            self.assertEqual(True,SettingFile.is_file())

    def test_SaveConfig(self):
        configObject = vc.config(self.testFileFolder)
        versa3dSetting = configObject.getSettings('Versa3dSettings')
        versa3dSetting.setSettingValue('Versa3d','unit','inch')

        configObject.saveSettings('Versa3dSettings',"newSetting")

        configObject2 = vc.config(self.testFileFolder)
        configObject2.readSettings('Versa3dSettings',"newSetting")
        versa3dSetting2 = configObject2.getSettings('Versa3dSettings')
        value = versa3dSetting2.getSettingValue('Versa3d','unit')
        self.assertEqual('inch', value)
        
    def tearDown(self):
        shutil.rmtree(self.testFileFolder)

def suite():
    suite = unittest.TestSuite()

    suite.addTest(TestConfig)
    return suite




