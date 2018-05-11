# -*- coding: utf-8 -*-

import configparser
import copy
import re
import vtk
import os
import fnmatch
from vtk.util import keys


def saveWrapperConfig(fun):
        
    def wrapped(self,name):
        output,fileName = fun(self,name)

        configFile = open(os.path.join(self._FolderPath,fileName+".ini"), 'w')
        configParse = configparser.ConfigParser()
        
        for key, OptionDic in output.items():
            configParse[key] = {}
            section = configParse[key]
            for optiontag,option in OptionDic.items():
                section[optiontag] = str(option.getValue())

        configParse.write(configFile)
        configFile.close()

        if(not fileName in self._FileDict):
            self._FileDict[fileName] = os.path.realpath(configFile.name)

    return wrapped

class Versa3dOption():
    def __init__(self,def_value):
        self._value = def_value

        self.label = ""
        self.tooltip = ""
        self.sidetext = ""
        self.category = ""
        self.subcategory = ""
        self.type = ""

        self.min = None
        self.max = None

        self.default_value = def_value

    def getValue(self):
        return self._value
    
    def setValue(self,val):
        self._value = val

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
    
    def globFile(self):

        fileDict = {}
        for file in os.listdir(self._FolderPath):
            if(fnmatch.fnmatch(file,'*.ini')):
                fileName ,fileExt = os.path.splitext(file)
                fileDict[fileName] =  os.path.join(self._FolderPath,file)
        
        return fileDict

    def getSettingValue(self,Section,tag):
        dic = getattr(self,Section)
        return dic[tag].getValue()
    
    def setSettingValue(self,Section,tag,value):
        dic = getattr(self,Section)
        dic[tag].setValue(value)

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
                    configdic = getattr(self, section)
                    configdic[key].setValue(self._unpackStr(configParse[section][key]))

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
    
    def writeFile(self,name):
        pass
    

class Versa3d_Settings(setting):
    def __init__(self,FolderPath):
        super().__init__(os.path.join(FolderPath,"Versa3dSettings"))

        self.Versa3d = {}

        self.Versa3d['unit'] = Versa3dOption('mm')
        self.Versa3d['machine'] = Versa3dOption('BMVlasea')
        self.Versa3d['printhead'] = Versa3dOption('Imtech')
        self.Versa3d['machinetype'] = Versa3dOption('BinderJet')
        self.Versa3d['gcodeflavor'] = Versa3dOption('BMVlasea')
        self.Versa3d['imgbmvlasealocalpath'] = Versa3dOption(True)


    @saveWrapperConfig
    def writeFile(self, name):
        output = {'Versa3d':self.Versa3d}
        return (output,name)

class Print_Settings(setting):
    def __init__(self,FolderPath):
        super().__init__(os.path.join(FolderPath,"PrintSettings"))
        #self.BinderJet = {'fill': FillEnum['full black'], 'layer_thickness': 0.1}
        self.BinderJet = {}

        FillEnum = {'fblack':'full black', 'fcheckerBoard':'checker board'}
        self.BinderJet['fill'] = Versa3dEnumOption(FillEnum,'fblack')
        self.BinderJet['layer_thickness'] = Versa3dOption(0.1)

    
    @saveWrapperConfig
    def writeFile(self, name):
        output = {'BinderJet': self.BinderJet }
        return (output, name)

class Printers_Settings(setting):
    def __init__(self,FolderPath):
        super().__init__(os.path.join(FolderPath,"PrinterSettings"))

        self.BMVlasea = {}
        self.BMVlasea['printbedsize'] = Versa3dOption([30.0,30.0])
        self.BMVlasea['buildheight'] = Versa3dOption(50.0)
        self.BMVlasea['gantryxyvelocity'] = Versa3dOption([100.0,100.0])
        self.BMVlasea['work_distance_roller_substrate'] = Versa3dOption(1.1)
        self.BMVlasea['printing_height_offset'] = Versa3dOption(0.05)
        self.BMVlasea['powder_loss'] = Versa3dOption(0.1)

        self.BMVlasea['feedbedvelocity'] = Versa3dOption(1)
        self.BMVlasea['feedbedvelocity'].setValue(10.0)

        self.BMVlasea['buildbedvelocity'] = Versa3dOption(10.0)
        self.BMVlasea['defaultprinthead'] = Versa3dOption(1)
        self.BMVlasea['defaultprintheadaddr'] = Versa3dOption(1)
        self.BMVlasea['rollerlinvel'] = Versa3dOption(10.0)
        self.BMVlasea['rollerrotvel'] = Versa3dOption(10.0)
        self.BMVlasea['feedbedsel'] = Versa3dOption(0)


    @saveWrapperConfig
    def writeFile(self, name):
        output = {'BMVlasea': self.BMVlasea}
        return (output, name)

class Printheads_Settings(setting):
    def __init__(self,FilePath):
        super().__init__(os.path.join(FilePath,"PrintHeadSettings"))

        self.Syringe = {}

        self.Syringe['syringe_motor_velocity'] = Versa3dOption(5)
        self.Syringe['syringepressure'] = Versa3dOption(20)
        self.Syringe['syringevacuum'] = Versa3dOption(3)
        self.Syringe['syringelinearvelocity'] = Versa3dOption(1)
        self.Syringe['syringeworkdistance'] = Versa3dOption(1)

        self.Imtech = {}
        self.Imtech['prinheadvppvoltage'] = Versa3dOption(1)
        self.Imtech['printheadpulsewidth'] = Versa3dOption(1)
        self.Imtech['printheadvelocity'] = Versa3dOption(25.4)
        self.Imtech['nprintswathe'] = Versa3dOption(1)
        self.Imtech['buffernumber'] = Versa3dOption(16)
        self.Imtech['buffersizelimit'] = Versa3dOption([150,-1])
        self.Imtech['dpi'] = Versa3dOption([600,600])

    @saveWrapperConfig
    def writeFile(self,name):
        output = {'Syringe': self.Syringe,'Imtech':self.Imtech}
        return (output,name)


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
    
    def getVersa3dSettings(self):
        return self.Versa3dSettings
    
    def getPrintSettings(self):
        return self.PrintSettings
    
    def getPrinterSettings(self):
        return self.PrinterSettings

    def getPrinterHeadSettings(self):
        return self.PrintHeadSettings

    def saveVersa3dSettings(self,name = "Default"):
        self.Versa3dSettings.writeFile(name)
    
    def savePrintSettings(self,name = "Default"):
        self.PrintSettings.writeFile(name)
    
    def savePrinterSettings(self,name = "Default"):
        self.PrinterSettings.writeFile(name)
    
    def savePrinterHeadSettings(self,name = "Default"):
        self.PrintHeadSettings.writeFile(name)
    
    def readVersa3dSettings(self,name = "Default"):
        self.Versa3dSettings.readConfigFile(name)
    
    def readPrintSettings(self,name = "Default"):
        self.PrintSettings.readConfigFile(name)
    
    def readPrinterSettings(self,name = "Default"):
        self.PrinterSettings.readConfigFile(name)
    
    def readPrinterHeadSettings(self,name = "Default"):
        self.PrintHeadSettings.readConfigFile(name)

    def saveConfig(self):
        self.Versa3dSettings.writeFile()
        self.PrintSettings.writeFile()
        self.PrinterSettings.writeFile()
        self.PrintHeadSettings.writeFile()
    
    def getVersa3dSetting(self,tag):
        return self.Versa3dSettings.getSettingValue('Versa3d',tag)
    
    def getMachineSetting(self,tag):
        MachineName = self.Versa3dSettings.getSettingValue('Versa3d','machine')
        return self.PrinterSettings.getSettingValue(MachineName,tag)
    
    def getPrintHeadSetting(self,tag):
        Printhead = self.Versa3dSettings.getSettingValue('Versa3d','printhead')
        return self.PrintHeadSettings.getSettingValue(Printhead,tag)
    
    def getPrintSetting(self,tag):
        ProcessType = self.Versa3dSettings.getSettingValue('Versa3d','machinetype')
        return self.PrintSettings.getSettingValue(ProcessType,tag)
           

    