import unittest
import src.lib.versa3dConfig as vc
from pathlib import Path
import os
import shutil

class TestConfig(unittest.TestCase):

    def setUp(self):
        self.testFileFolder = './configtest'
        os.mkdir(self.testFileFolder)

    def test_ConfigCreation(self):
        configObject = vc.config(self.testFileFolder)

        Versa3dIniFile = Path(os.path.join(self.testFileFolder,vc.Versa3dIniFileName))
        SliceIniFile = Path(os.path.join(self.testFileFolder,vc.SliceIniFileName))
        PrintheadIniFile= Path(os.path.join(self.testFileFolder,vc.PrintHeadIniFileName))
        PrinterIniFile = Path(os.path.join(self.testFileFolder,vc.PrinterIniFileName))
        #check if file created
        self.assertEqual(True, Versa3dIniFile.is_file())
        self.assertEqual(True,SliceIniFile.is_file())
        self.assertEqual(True,PrintheadIniFile.is_file())
        self.assertEqual(True,PrinterIniFile.is_file())
    
    def test_ConfigGetValue(self):
        configObject = vc.config(self.testFileFolder)

        versa3dSetting = configObject.getVersa3dSettings()
        printerSetting = configObject.getPrinterSettings()
        printheadSetting = configObject.getPrinterHeadSettings()
        SliceSetting = configObject.getSlicingSettings()

        UnitValue = versa3dSetting.getSettingValue('Versa3d','unit')
        self.assertEqual('mm',UnitValue)

        printBedValue = printerSetting.getSettingValue('BMVlasea','printbedsize')
        self.assertEqual([30,30], printBedValue)

        buffersizeLimit = printheadSetting.getSettingValue('Imtech','BufferSizeLimit')
        self.assertEqual([150,-1], buffersizeLimit)

        FillValue = SliceSetting.getSettingValue('BinderJet','layer_thickness')
        self.assertEqual(0.1, FillValue)

        gantryXYVelocity = printerSetting.getSettingValue('BMVlasea','gantryXYVelocity')
        self.assertEqual([100,100],gantryXYVelocity)

        printBedValue = configObject.getMachineSetting('printbedsize')
        self.assertEqual([30,30], printBedValue)
 
    def test_ModifyConfig(self):
        configObject = vc.config(self.testFileFolder)

        versa3dSetting = configObject.getVersa3dSettings()

        versa3dSetting.setSettingValue('Versa3d','unit','inch')

        value = versa3dSetting.getSettingValue('Versa3d','unit')

        self.assertEqual('inch', value)

    def test_SaveConfig(self):
        configObject = vc.config(self.testFileFolder)
        versa3dSetting = configObject.getVersa3dSettings()
        versa3dSetting.setSettingValue('Versa3d','unit','inch')

        configObject.saveConfig()

        configObject2 = vc.config(self.testFileFolder)
        versa3dSetting2 = configObject2.getVersa3dSettings()
        value = versa3dSetting2.getSettingValue('Versa3d','unit')
        self.assertEqual('inch', value)
        
    def tearDown(self):
        shutil.rmtree(self.testFileFolder)

def suite():
    suite = unittest.TestSuite()

    suite.addTest(TestConfig)
    return suite




