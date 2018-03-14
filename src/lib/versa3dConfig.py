# -*- coding: utf-8 -*-

import configparser
import copy
import re
import vtk
from vtk.util import keys

FillEnum = ['black', 'checker_board']
Default_Slice_Setting = {'fill': FillEnum[0], 'layer_thickness': 0.1, 'dpi': [600,600],'BufferSizeLimit': [150,-1]}
Default_Printer_Setting = {'printbedsize': [200.0,200.0], 'buildheight':200.0}
Default_Versa3d_Setting = {'unit':'mm'}

class config():
    
    def __init__(self, FilePath):
        
        self._FilePath = FilePath

        self.SlicingSettings = {}
        self.Versa3dSettings ={}
        self.PrinterSettings = {}

        self.ActorKey = keys.MakeKey(keys.StringKey,"Type","Actor")

        self._configFile = None
        self._configParse = None
        try:
            self.readConfigFile()
        except IOError:
            self.createConfigFile()
    
    def getKey(self,Name,Class):
        if(Name =="Type" and Class == "Actor"):
            return self.ActorKey
        else:
            return None
            
    def createConfigFile(self):
        #create config        
        self.setDefaultValue()
        self.saveConfig()
        
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
                configdic[key] = self._unpackStr(self._configParse[section][key])

        self._configFile.close()
    
    def _unpackStr(self,configString):
        if(self._is_number(configString)):
            return float(configString)
        elif(self._is_array(configString)):
            return self._convertStrArray(configString)
        else:
            return configString

    def _is_number(self,num):
        try:
            float(num)
            return True
        except ValueError:
            return False

    def _is_array(self,arrayStr):
        p = re.compile('^\[.*\]')
        if(p.match(arrayStr)!= None):
            return True
        else:
            return False
    
    def _convertStrArray(self,Str):
        strippedStr = Str[1:-1]
        StrArray = strippedStr.split(",")

        newArray = []
        for element in StrArray:
            if(self._is_number(element)):
                newArray.append(float(element))
            else:
                newArray.append(element)
        
        return newArray

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
        if(configKey in self.Versa3dSettings.keys()):
            self.Versa3dSettings[configKey] = value
            return self.Versa3dSettings[configKey] 
        elif(configKey in self.PrinterSettings.keys()):
            self.PrinterSettings[configKey] = value
            return self.PrinterSettings[configKey]
        elif(configKey in self.SlicingSettings.keys()):
            self.SlicingSettings[configKey] = value
            return self.SlicingSettings[configKey]
        else:
            return ''
    
    def saveConfig(self):
        self._configParse = configparser.ConfigParser()

        self._configParse['Versa3dSettings'] = self.Versa3dSettings      
        self._configParse['SlicingSettings'] = self.SlicingSettings
        self._configParse['PrinterSettings'] = self.PrinterSettings
        
        with open(self._FilePath, 'w') as self._configFile:
            self._configParse.write(self._configFile)
        
        self._configFile.close()
    

    

    