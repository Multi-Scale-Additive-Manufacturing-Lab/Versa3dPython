# -*- coding: utf-8 -*-

import configparser
import copy

FillEnum = ['Black', 'CheckerBoard']
Default_Slice_Setting = {'Fill': FillEnum[0], 'layer_thickness': 0.1}
Default_Printer_Setting = {'PrintBedSize': [10,10]}
Default_Versa3d_Setting = {'Unit':'mm'}

class config():
    
    def __init__(self, FilePath):
        
        self._FilePath = FilePath

        self.SlicingSettings = {}
        self.Versa3dSettings ={}
        self.PrinterSettings = {}

        try:
            self.readConfigFile()
        except IOError:
            self.createConfigFile()
            
    def createConfigFile(self):
        #create config
        self._configParse = configparser.ConfigParser()
        self.setDefaultValue()

        self._configParse['Versa3dSettings'] = self.Versa3dSettings      
        self._configParse['SlicingSettings'] = self.SlicingSettings
        self._configParse['PrinterSettings'] = self.PrinterSettings
        
        with open(self._FilePath, 'w') as self._configFile:
            self._configParse.write(self._configFile)
        
        self._configFile.close()
        
    def setDefaultValue(self):
        self.SlicingSettings = copy.deepcopy(Default_Slice_Setting)
        self.Versa3dSettings = copy.deepcopy(Default_Versa3d_Setting)
        self.PrinterSettings = copy.deepcopy(Default_Printer_Setting)
    
    def readConfigFile(self):
        self._configFile = open(self._FilePath, 'r')
        self._configParse = configparser.ConfigParser()
        
        self._configParse.read_file(self._configFile)

        for section in self._configParse.sections():
            for key in self._configParse[section]:
                configdic = getattr(self, section)
                configdic[key] = self._configParse[section][key]

        self._configFile.close() 
    
    def getValue(self,configKey):
        
        if(configKey in self.Versa3dSettings.keys()):
            return self.Versa3dSettings[configKey]
        elif(configKey in self.PrinterSettings.keys()):
            return self.PrinterSettings[configKey]
        elif(configKey in self.SlicingSettings.keys()):
            return self.SlicingSettings[configKey]
        else:
            return ''

    def setValue(self, configKey,value):
        pass
    
    def saveConfig(self):
        pass
    

    

    