# -*- coding: utf-8 -*-

import configparser
import copy
import re
import vtk
import os
import fnmatch
from vtk.util import keys

FillEnum = ['black', 'checker_board']

def saveWrapperConfig(fun):
        
    def wrapped(self,name):
        output,fileName = fun(self,name)

        configFile = open(os.path.join(self._FolderPath,fileName+".ini"), 'w')
        configParse = configparser.ConfigParser()
        
        for key, value in output.items():
            configParse[key] = value

        configParse.write(configFile)
        configFile.close()

        if(not fileName in self._FileDict):
            self._FileDict[fileName] = os.path.realpath(configFile.name)

    return wrapped

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
        return dic[tag]
    
    def setSettingValue(self,Section,tag,value):
        dic = getattr(self,Section)
        dic[tag] = value

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
                    configdic[key] = self._unpackStr(configParse[section][key])

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
        self.Versa3d = {'unit':'mm', 'Machine':'BMVlasea','PrintHead':'Imtech',
                        'MachineType':'BinderJet','gcodeFlavor':'BMVlasea','ImgBMVLaseaLocalPath':True}

    @saveWrapperConfig
    def writeFile(self, name):
        output = {'Versa3d':self.Versa3d}
        return (output,name)

class Print_Settings(setting):
    def __init__(self,FolderPath):
        super().__init__(os.path.join(FolderPath,"PrintSettings"))
        self.BinderJet = {'fill': FillEnum[0], 'layer_thickness': 0.1}
    
    @saveWrapperConfig
    def writeFile(self, name):
        output = {'BinderJet': self.BinderJet }
        return (output, name)

class Printers_Settings(setting):
    def __init__(self,FolderPath):
        super().__init__(os.path.join(FolderPath,"PrinterSettings"))
        self.BMVlasea = {'printbedsize': [30.0,30.0], 'buildheight':50.0, 'gantryXYVelocity':[100.0,100.0],
                         'Work_Distance_Roller_Substrate':1.1,'Printing_Height_Offset':0.05,'Powder_Loss':0.1,
                         'feedBedVelocity':10.0, 'buildBedVelocity':10.0,
                         'DefaultFeedBed':1,'DefaultPrinthead':1,'DefaultPrintHeadAddr':1,
                         'RollerLinVel':10.0,'RollerRotVel':10.0,'FeedBedSel':0}
    
    @saveWrapperConfig
    def writeFile(self, name):
        output = {'BMVlasea': self.BMVlasea}
        return (output, name)

class Printheads_Settings(setting):
    def __init__(self,FilePath):
        super().__init__(os.path.join(FilePath,"PrintHeadSettings"))
        self.Syringe = {'Syringe_Motor_Velocity':5,'SyringePressure':20,'SyringeVacuum':3,
                            'SyringeLinearVelocity':1,'SyringeWorkDistance':1}

        self.Imtech =  {'PrinheadVPPVoltage':1,'PrintheadPulseWidth':1,
                        'PrintheadVelocity':25.4,'NPrintSwathe':1,'BufferNumber':16,'BufferSizeLimit': [150,-1],'dpi': [600,600]}
    
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
        MachineName = self.Versa3dSettings.getSettingValue('Versa3d','Machine')
        return self.PrinterSettings.getSettingValue(MachineName,tag)
    
    def getPrintHeadSetting(self,tag):
        Printhead = self.Versa3dSettings.getSettingValue('Versa3d','PrintHead')
        return self.PrintHeadSettings.getSettingValue(Printhead,tag)
    
    def getPrintSetting(self,tag):
        ProcessType = self.Versa3dSettings.getSettingValue('Versa3d','MachineType')
        return self.PrintSettings.getSettingValue(ProcessType,tag)
           

    