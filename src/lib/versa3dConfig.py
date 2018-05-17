# -*- coding: utf-8 -*-

import configparser
import copy
import re
import vtk
import os
import fnmatch
from vtk.util import keys


class Versa3dOption():
    def __init__(self,def_value):
        self._value = def_value

        self.label = ""
        self.tooltip = ""
        self.sidetext = ""
        self.category = ""
        self.subcategory = ""
        self.type = ""
        self._QObject = None

        self.min = None
        self.max = None

        self.default_value = def_value

    def getValue(self):
        return self._value
    
    def setValue(self,val):
        self._value = val
        return self._value
    
    def updateValue(self):
        pass

class Versa3dEnumOption(Versa3dOption):
    def __init__(self,Enum,default_val):
        super().__init__(default_val)

        self._list = Enum
    
    def getEnum(self):
        return self._list

class setting():

    def __init__(self,FolderPath):

        if(not os.path.isdir(FolderPath)):
            os.mkdir(FolderPath)

        self._FolderPath = FolderPath
        self._FileDict = self.globFile()
        self._ConfigName = 'Default'
        self._settingList = {}
    
    def globFile(self):

        fileDict = {}
        for file in os.listdir(self._FolderPath):
            if(fnmatch.fnmatch(file,'*.ini')):
                fileName ,fileExt = os.path.splitext(file)
                fileDict[fileName] =  os.path.join(self._FolderPath,file)
        
        return fileDict

    def getSettingValue(self,tag):
        if tag in self._settingList:
            return self._settingList[tag].getValue()
        else:
            return None
    
    def setSettingValue(self,tag,value):
        if tag in self._settingList:
            return self._settingList[tag].setValue(value)
        else:
            return None

    def readConfigFile(self,Name = None):

        if(Name == None):
            Name = self._ConfigName
        
        if(Name in self._FileDict and not Name == "Default"):
            filePath = self._FileDict[Name]

            configFile = open(filePath, 'r')
            configParse = configparser.ConfigParser()
            
            configParse.read(filePath)

            for section in configParse.sections():
                for key in configParse[section]:

                    if key in self._settingList:
                        self._settingList[key].setValue(self._unpackStr(configParse[section][key]))

            configFile.close()
    
    def getListOfConfig(self):
        return self._FileDict.keys()
    
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
    
    def writeFile(self,fileName):
        configFile = open(os.path.join(self._FolderPath,fileName+".ini"), 'w')
        configParse = configparser.ConfigParser()
        
        for key, item in self._settingList.items():
            category = item.category
            
            if(not configParse.has_section(category)):
                configParse.add_section(category)

            configParse[category][key] = str(item.getValue())

        configParse.write(configFile)
        configFile.close()

        if(not fileName in self._FileDict):
            self._FileDict[fileName] = os.path.realpath(configFile.name)
    

class Versa3d_Settings(setting):
    def __init__(self,FolderPath):
        super().__init__(os.path.join(FolderPath,"Versa3dSettings"))

        self._settingList['unit'] = Versa3dOption('mm')
        self._settingList['unit'].category = 'general'

        self._settingList['machine'] = Versa3dOption('BMVlasea')
        self._settingList['machine'].category = 'general'

        self._settingList['printhead'] = Versa3dOption('Imtech')
        self._settingList['printhead'].category = 'general'

        self._settingList['machinetype'] = Versa3dOption('BinderJet')
        self._settingList['machinetype'].category = 'general'

        self._settingList['gcodeflavor'] = Versa3dOption('BMVlasea')
        self._settingList['gcodeflavor'].category = 'general'

        self._settingList['imgbmvlasealocalpath'] = Versa3dOption(True)
        self._settingList['imgbmvlasealocalpath'].category = 'general'


class Print_Settings(setting):
    def __init__(self,FolderPath):
        super().__init__(os.path.join(FolderPath,"PrintSettings"))

        FillEnum = {'fblack':'full black', 'fcheckerBoard':'checker board'}
        self._settingList['fill'] = Versa3dEnumOption(FillEnum,'fblack')
        self._settingList['fill'].label = 'Fill Pattern'
        self._settingList['fill'].category = 'BinderJet'
        self._settingList['fill'].subcategory = 'InFill'
        self._settingList['fill'].type = 'StringEnum'

        self._settingList['layer_thickness'] = Versa3dOption(0.1)
        self._settingList['layer_thickness'].label = 'layer thickness'
        self._settingList['layer_thickness'].category = 'BinderJet'
        self._settingList['layer_thickness'].subcategory = 'InFill'
        self._settingList['layer_thickness'].type = 'float'
        self._settingList['layer_thickness'].sidetext = 'mm'


class Printers_Settings(setting):
    def __init__(self,FolderPath):
        super().__init__(os.path.join(FolderPath,"PrinterSettings"))

        self._settingList['printbedsize'] = Versa3dOption([30.0,30.0])
        self._settingList['printbedsize'].category = "BMVLasea"

        self._settingList['buildheight'] = Versa3dOption(50.0)
        self._settingList['buildheight'].category = "BMVLasea"

        self._settingList['gantryxyvelocity'] = Versa3dOption([100.0,100.0])
        self._settingList['gantryxyvelocity'].category = "BMVLasea"

        self._settingList['work_distance_roller_substrate'] = Versa3dOption(1.1)
        self._settingList['work_distance_roller_substrate'].category = "BMVLasea"

        self._settingList['printing_height_offset'] = Versa3dOption(0.05)
        self._settingList['printing_height_offset'].category = "BMVLasea"
        
        self._settingList['powder_loss'] = Versa3dOption(0.1)
        self._settingList['powder_loss'].category = "BMVLasea"

        self._settingList['feedbedvelocity'] = Versa3dOption(1)
        self._settingList['feedbedvelocity'].setValue(10.0)
        self._settingList['feedbedvelocity'].category = "BMVLasea"

        self._settingList['buildbedvelocity'] = Versa3dOption(10.0)
        self._settingList['buildbedvelocity'].category = "BMVLasea"

        self._settingList['defaultprinthead'] = Versa3dOption(1)
        self._settingList['defaultprinthead'].category = "BMVLasea"

        self._settingList['defaultprintheadaddr'] = Versa3dOption(1)
        self._settingList['defaultprintheadaddr'].category = "BMVLasea"

        self._settingList['rollerlinvel'] = Versa3dOption(10.0)
        self._settingList['rollerlinvel'].category = "BMVLasea"

        self._settingList['rollerrotvel'] = Versa3dOption(10.0)
        self._settingList['rollerrotvel'].category = "BMVLasea"

        self._settingList['feedbedsel'] = Versa3dOption(0)
        self._settingList['feedbedsel'].category = "BMVLasea"


class Printheads_Settings(setting):
    def __init__(self,FilePath):
        super().__init__(os.path.join(FilePath,"PrintHeadSettings"))
        
        self._settingList['syringe_motor_velocity'] = Versa3dOption(5)
        self._settingList['syringe_motor_velocity'].category = "Syringe"

        self._settingList['syringepressure'] = Versa3dOption(20)
        self._settingList['syringepressure'].category = "Syringe"

        self._settingList['syringevacuum'] = Versa3dOption(3)
        self._settingList['syringevacuum'].category = "Syringe"

        self._settingList['syringelinearvelocity'] = Versa3dOption(1)
        self._settingList['syringelinearvelocity'].category = "Syringe"

        self._settingList['syringeworkdistance'] = Versa3dOption(1)
        self._settingList['syringeworkdistance'].category = "Syringe"

        self._settingList['prinheadvppvoltage'] = Versa3dOption(1)
        self._settingList['prinheadvppvoltage'].category = "Imtech"

        self._settingList['printheadpulsewidth'] = Versa3dOption(1)
        self._settingList['printheadpulsewidth'].category = "Imtech"

        self._settingList['printheadvelocity'] = Versa3dOption(25.4)
        self._settingList['printheadvelocity'].category = "Imtech"

        self._settingList['nprintswathe'] = Versa3dOption(1)
        self._settingList['nprintswathe'].category = "Imtech"

        self._settingList['buffernumber'] = Versa3dOption(16)
        self._settingList['buffernumber'].category = "Imtech"

        self._settingList['buffersizelimit'] = Versa3dOption([150,-1])
        self._settingList['buffersizelimit'].category = "Imtech"

        self._settingList['dpi'] = Versa3dOption([600,600])
        self._settingList['dpi'].category = "Imtech"


class config():
    
    def __init__(self,ConfigFolderPath):

        self.Versa3dSettings = Versa3d_Settings(ConfigFolderPath)
        self.PrintSettings = Print_Settings(ConfigFolderPath)
        self.PrinterSettings = Printers_Settings(ConfigFolderPath)
        self.PrintHeadSettings = Printheads_Settings(ConfigFolderPath)

        self._listOfSetting = [self.Versa3dSettings,self.PrintSettings,self.PrinterSettings,self.PrintHeadSettings]
        self.ActorKey = keys.MakeKey(keys.StringKey,"Type","Actor")

        for setting in self._listOfSetting:
            setting.readConfigFile()

    def getKey(self,Name,Class):
        if(Name =="Type" and Class == "Actor"):
            return self.ActorKey
        else:
            return None
    
    def getSettings(self,Name):
        return getattr(self,Name)
    
    def saveSettings(self,SettingName,FileName = "Default"):
        section = getattr(self,SettingName)
        section.writeFile(FileName)

    def saveAll(self,name = "Default"):
        self.Versa3dSettings.writeFile(name)
        self.PrintSettings.writeFile(name)
        self.PrinterSettings.writeFile(name)
        self.PrintHeadSettings.writeFile(name)
    
    def readSettings(self,SettingName,name):
        section = getattr(self,SettingName)
        section.readConfigFile(name)
    
    def getVersa3dSetting(self,tag):
        return self.Versa3dSettings.getSettingValue(tag)
    
    def getMachineSetting(self,tag):
        return self.PrinterSettings.getSettingValue(tag)
    
    def getPrintHeadSetting(self,tag):
        return self.PrintHeadSettings.getSettingValue(tag)
    
    def getPrintSetting(self,tag):
        return self.PrintSettings.getSettingValue(tag)
           

    