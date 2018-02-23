# -*- coding: utf-8 -*-

import configparser

FillDict = {'Black': 'ImtechBlack', 'CheckerBoard': 'ImtechCheckerBoard'}

class config(object):
    pass

class configParser():
    
    def __init__(self, FilePath):
        
        self._FilePath = FilePath
        self.config = config()
        
        try:
            self.readConfigFile()
        except IOError:
            self.createConfigFile()
            
    def createConfigFile(self):
        #create config
        self._configParse = configparser.ConfigParser()
        self.setDefaultValue()

        self._configParse['Versa3dSetting'] = {'Unit': self.config.Unit}        
        self._configParse['Slicing_Config'] = {'Fill': self.config.Fill,'layer_thickness': self.config.layer_thickness}
        
        with open(self._FilePath, 'w') as self._configFile:
            self._configParse.write(self._configFile)
        
        self._configFile.close()
        
    def setDefaultValue(self):
        setattr(self.config,'Unit','mm')
        setattr(self.config,'Fill',FillDict['Black'])
        setattr(self.config,'layer_thickness',0.1)
    
    def readConfigFile(self):
        self._configFile = open(self._FilePath, 'r')
        self._configParse = configparser.ConfigParser()
        
        self._configParse.read_file(self._configFile)
        
        for section in self._configParse.sections():
            for key in self._configParse[section]:
                setattr(self.config,key,self._configParse[section][key])
                
                
        self._configFile.close() 
    
        

if __name__ == "__main__":
    test = configParser('test.ini')
    config = test.config
    
    print(config.Unit)