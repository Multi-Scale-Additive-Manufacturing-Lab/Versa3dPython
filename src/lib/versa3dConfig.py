# -*- coding: utf-8 -*-

import configparser
import copy
import re
import vtk
import os
from vtk.util import keys

FillEnum = ['black', 'checker_board']

Versa3dIniFileName = "versa3dConfig.ini"
SliceIniFileName = "sliceConfig.ini"
PrinterIniFileName = "PrinterConfig.ini"
PrintHeadIniFileName = "PrintHeadConfig.ini"

class setting():

    def __init__(self,FilePath):
        self._FilePath = FilePath

    def getSettingValue(self,Section,tag):
        dic = getattr(self,Section)
        return dic[tag]
    
    def setSettingValue(self,Section,tag,value):
        dic = getattr(self,Section)
        dic[tag] = value

    def readConfigFile(self):
        configFile = open(self._FilePath, 'r')
        configParse = configparser.ConfigParser()
        
        configParse.read(self._FilePath)

        for section in configParse.sections():
            for key in configParse[section]:
                configdic = getattr(self, section)
                configdic[key] = self._unpackStr(configParse[section][key])

        configFile.close()
    
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
    
    def saveConfig(self):
        pass

class Versa3d_Settings(setting):
    def __init__(self,FilePath):
        super().__init__(FilePath)
        self.Versa3d = {'unit':'mm'}

    def saveConfig(self):

        configFile = open(self._FilePath, 'w')
        configParse = configparser.ConfigParser()

        configParse['Versa3d'] = self.Versa3d
        configParse.write(configFile)
        configFile.close()


class Slice_Settings(setting):
    def __init__(self,FilePath):
        super().__init__(FilePath)
        self.BinderJet = {'fill': FillEnum[0], 'layer_thickness': 0.1}
    
    def saveConfig(self):

        configFile = open(self._FilePath, 'w')
        configParse = configparser.ConfigParser()

        configParse['BinderJet'] = self.BinderJet

        configParse.write(configFile)
        configFile.close()

class Printers_Settings(setting):
    def __init__(self,FilePath):
        super().__init__(FilePath)

        self.BMVlasea = {'printbedsize': [30.0,30.0], 'buildheight':50.0,'gcodeFlavor':'VlaseaBM',
                         'gantryXYVelocity':[100.0,100.0],'ZVelocity':[10.0,10.0],'CarriageVelocity':20,
                         'feedBedVelocity':10.0, 'buildBedVelocity':10.0, 'rollerVelocity':50, 'PrintHeadVelocity':25.4,
                         'Work_Distance_Roller_Substrate':1.1,'Printing_Height_Offset':0.05,'DefaultFeedBed':1,'DefaultPrinthead':1}
    def saveConfig(self):

        configFile = open(self._FilePath, 'w')
        configParse = configparser.ConfigParser()

        configParse['BMVlasea'] = self.BMVlasea

        configParse.write(configFile)
        configFile.close()

class Printheads_Settings(setting):
    def __init__(self,FilePath):
        super().__init__(FilePath)

        
        self.Syringe = {'Syringe_Motor_Velocity':5,'SyringePressure':20,'SyringeVacuum':3,
                            'SyringeLinearVelocity':1,'SyringeWorkDistance':1}

        self.Imtech =  {'PrinheadVPPVoltage':1,'PrintheadPulseWidth':1,
                        'PrintheadVelocity':25.4,'NPrintSwathe':1,'BufferSizeLimit': [150,-1],'dpi': [600,600]}
    
    def saveConfig(self):

        configFile = open(self._FilePath, 'w')
        configParse = configparser.ConfigParser()

        configParse['Syringe'] = self.Syringe
        configParse['Imtech'] = self.Imtech

        configParse.write(configFile)
        configFile.close()


class config():
    
    def __init__(self,ConfigFolderPath):

        self.Versa3dSettings = Versa3d_Settings(os.path.join(ConfigFolderPath,Versa3dIniFileName))
        self.SlicingSettings = Slice_Settings(os.path.join(ConfigFolderPath,SliceIniFileName))
        self.PrinterSettings = Printers_Settings(os.path.join(ConfigFolderPath,PrinterIniFileName))
        self.PrintHeadSettings = Printheads_Settings(os.path.join(ConfigFolderPath,PrintHeadIniFileName))

        self._listOfSetting = [self.Versa3dSettings,self.SlicingSettings,self.PrinterSettings,self.PrintHeadSettings]
        self.ActorKey = keys.MakeKey(keys.StringKey,"Type","Actor")

        for setting in self._listOfSetting:
            try:
                setting.readConfigFile()
            except IOError:
                setting.saveConfig()
    
    def getKey(self,Name,Class):
        if(Name =="Type" and Class == "Actor"):
            return self.ActorKey
        else:
            return None
    
    def getVersa3dSettings(self):
        return self.Versa3dSettings
    
    def getSlicingSettings(self):
        return self.SlicingSettings
    
    def getPrinterSettings(self):
        return self.PrinterSettings

    def getPrinterHeadSettings(self):
        return self.PrintHeadSettings
    def saveConfig(self):
        self.Versa3dSettings.saveConfig()
        self.SlicingSettings.saveConfig()
        self.PrinterSettings.saveConfig()
        self.PrintHeadSettings.saveConfig()

    


    

    

    