import vtk
from vtk.util.numpy_support import vtk_to_numpy
from src.lib.versa3dConfig import config
from src.lib.bmpwrite import BmpWriter
from lxml import etree
from lxml.builder import E
from copy import deepcopy
import math
import os
import string
import numpy

def gcodeFactory(type, config):
    
    if('VlaseaBM' == type):
        return gcodeWriterVlaseaBM(config)
    else:
        return None

class gcodeWriter():
    def __init__(self,config):
        self._config =config

class gcodeWriterVlaseaBM(gcodeWriter):

    def __init__(self,config, FolderPath):
        """gcodeWriterVlaseaBM Constructor
        
        :param config: config class
        :type config: config object
        :param FolderPath: Gcode Output Folder
        :type FolderPath: String
        """
        super().__init__(config)
        self._Folderpath = FolderPath
        self._Slicer = None

        self.gantryXYVelocity = config.getMachineSetting('gantryxyvelocity')
        self.H = config.getMachineSetting('work_distance_roller_substrate')
        self.S = config.getMachineSetting('powder_loss')
        self.W = config.getMachineSetting('printing_height_offset')
        self.feedBedVelocity = config.getMachineSetting('feedbedvelocity')
        self.buildBedVelocity = config.getMachineSetting('buildbedvelocity')
        self.DefaultPrintHead = config.getMachineSetting('defaultprinthead')
        self.DefaultPrintVelocity = config.getPrintHeadSetting('printheadvelocity')
        self.DefaultPrintHeadAddr = config.getMachineSetting('defaultprintheadaddr')
        self.BuildBedSize = config.getMachineSetting('printbedsize')

        self.NumberOfBuffer = config.getPrintHeadSetting('buffernumber')
        self.XImageSizeLimit = config.getPrintHeadSetting('buffersizelimit')[0]

        self.FeedBedSel = config.getMachineSetting('feedbedsel')

        self.rollerLinVel = config.getMachineSetting('rollerlinvel')
        self.rollerRotVel = config.getMachineSetting('rollerrotvel')
        
        self.Thickness = config.getPrintSetting('layer_thickness')
        self.AbsPathBMVlaseaComputerBool = config.getVersa3dSetting('imgbmvlasealocalpath')
        self.AbsPathBMVlaseaComputer = config.getVersa3dSetting('imgbmlasealocalpathstr')
        
        self.dpi = config.getPrintHeadSetting('dpi')

        self.imgMarginSize = 15

    def SetInput(self,slicer):
        """Set Input slicer
        
        :param slicer: slicer class
        :type slicer: VoxelSlicer object
        """
        self._Slicer = slicer   

    def generateGCode(self):

        SliceStack = self._Slicer.getBuildVolume()
        
        imageFolder = os.path.join(self._Folderpath,"Image")
        os.mkdir(imageFolder)

        count = 1
        for IndividualSlice in SliceStack:
            OriginalImg = IndividualSlice.getImage()

            self.XMLRoot = self.BuildSequenceCluster(0)

            self.generateGCodeLayer(count,OriginalImg,imageFolder)

            xmlFileName = "Layer.%d.xml"%(count)
            count = count + 1
            xmlFullPath = os.path.join(self._Folderpath,xmlFileName)

            tree = etree.ElementTree(self.XMLRoot)
            tree.write(xmlFullPath, pretty_print=True)


    def BuildSequenceCluster(self,Dimsize):
        root = (E.Array(
                    E.Name("Build Sequence"),
                    E.Dimsize(str(Dimsize))
                )
            )
        
        return root
    
    def imageWriter(self, Slice, imgFullPath):
        size = Slice.GetDimensions()
        origin = list(Slice.GetOrigin())

        bmpWriter = BmpWriter()
        bmpWriter.set_file_name(imgFullPath)
        bmpWriter.SetInputDataObject(0, Slice)
        bmpWriter.set_split_img_true(self.imgMarginSize,self.XImageSizeLimit)

        OffsetRealCoord = ((150.0-2*self.imgMarginSize)/self.dpi[0])*25.4

        NumSubImage = math.ceil(size[1]/self.XImageSizeLimit)
        listofPosition = []
        pos = [5+origin[0],38+origin[1]]

        for i in range(0,NumSubImage):
            listofPosition.append(pos.copy())
            pos[0] += OffsetRealCoord
        
        bmpWriter.Update()

        return listofPosition

    def generateGCodeLayer(self,layerNum,imgSlice,imageFolder):

        defaultStep = self.create_default_Step()

        origin = imgSlice.GetOrigin()
        (xDim, yDim,zDim) = imgSlice.GetDimensions()

        listOfLetter = string.ascii_uppercase

        imgfileName = "slice_{0:d}.bmp".format(layerNum)
        imgFullPath = os.path.join(imageFolder,imgfileName)

        listofPosition = self.imageWriter(imgSlice,imgFullPath)

        if(self.AbsPathBMVlaseaComputerBool):
            baseFolder = "{}\{}\image\\".format(self.AbsPathBMVlaseaComputer,os.path.basename(self._Folderpath))
            imgPath = baseFolder+imgfileName
        else:
            baseFolder = os.path.join("./","image")
            imgPath = os.path.join(baseFolder,imgfileName)

        NumberOfImage = len(listofPosition)

        if(NumberOfImage):
            #step 0 - turn ON printhead and get ready to print buffer BNumber
            textStr = "%T{},{},{}".format(str(1).zfill(2),65,NumberOfImage)
            step0 = self.ImtechPrintHead(True,8,1,0,0,0,0,textStr,self.DefaultPrintHeadAddr,imgPath)
            self.makeStep(defaultStep,step0,"step 0 - turn ON printhead and save font")
        
        #step 1 - move gantry to X1 = 0 
        step1 = self.Gantry(True,0,3,[0,0],0,self.gantryXYVelocity[0],"")
        self.makeStep(defaultStep,step1,"step 1 - move gantry to X1 = 0")

        #step 2 - move to Y = 0
        step2 = self.Gantry(True,0,3,[0,0],2,self.gantryXYVelocity[1],"")
        self.makeStep(defaultStep,step2,"step 2 - move to Y = 0")

        #step 3 - turn on roller
        step3 = self.Roller(True,6,1,self.rollerRotVel)
        self.makeStep(defaultStep,step3,"step 3 - turn on roller")
        
        #step 4 - material handling raise feed bed by = H+T+S
        step4 = self.MaterialHandling(True,2,2,self.H+self.Thickness+self.S,self.FeedBedSel,self.feedBedVelocity,0,0)
        self.makeStep(defaultStep,step4,"step 4 - material handling raise feed bed by = H+T+S")
        
        #step 5 - material handling raise build bed by = H-T
        step5 = self.MaterialHandling(True,2,2,self.H-self.Thickness,3,self.buildBedVelocity,0,0)
        self.makeStep(defaultStep,step5,"step 5 - material handling raise build bed by = H-T")
        
        #step 6 - spread the powder by moving in X-coordinate 300
        step6 = self.Gantry(True,0,3,[300,0],0,self.rollerLinVel,"")
        self.makeStep(defaultStep,step6,"step 6 - spread the powder by moving in X-coordinate 300")
        
        #step 7 - turn off roller
        step7 = self.Roller(True,6,1,0)
        self.makeStep(defaultStep,step7,"step 7 - turn off roller")
        
        #step 8 - lower build bed by -(H+W)
        step8 = self.MaterialHandling(True,2,2,(-1)*(self.H+self.W),3, self.buildBedVelocity,0,0)
        self.makeStep(defaultStep,step8,"step 8 - lower build bed by -(H+W)")
        
        #step 9 - lower feed bed by -(H+W)
        step9 = self.MaterialHandling(True,2,2,(-1)*(self.H+self.W),self.FeedBedSel,self.feedBedVelocity,0,0)
        self.makeStep(defaultStep,step9,"step 9 - lower feed bed by -(H+W)")

        for i in range(0,NumberOfImage):
            position = listofPosition[i]
            #step 10 allign printhead with the printing area - move to lower left corner of image
            step10 = self.Gantry(True,0,3,[0,43],2,self.gantryXYVelocity[1],"")
            self.makeStep(defaultStep,step10,"step 10 align to y : {}".format(43))

            #step 11 allign printhead with the printing area 
            step11 = self.Gantry(True,0,3,[position[0],0],0,self.gantryXYVelocity[0],"")
            self.makeStep(defaultStep,step11,"step 11 align to x : {}".format(position[0]))

            #step 12 turn ON printhead and get ready to print buffer i
            step12 = self.ImtechPrintHead(True,8,5,0,0,i,0,0,self.DefaultPrintHeadAddr,1)
            self.makeStep(defaultStep,step12,"step 12 print buffer: {}".format(i))

            #step 13 execute printing motion in Y direction - move to right
            step13 = self.Gantry(True,0,3,[0,70],2,self.DefaultPrintVelocity,"")
            self.makeStep(defaultStep,step13,"step 13 move to y: 70")
            
        #step 14 move back to origin in Y -direction Y=0(former step 16)
        step14 = self.Gantry(True,0,3,[0,0],2,self.gantryXYVelocity[1],"")
        self.makeStep(defaultStep,step14,"step 14 move back to origin y")

        #step 15 move back to origin in X-direction X=0 
        step15 = self.Gantry(True,0,3,[0,0],0,self.gantryXYVelocity[0],"")
        self.makeStep(defaultStep,step15,"step 15 move back to origin x")
        
        #step 16 raise build bed
        step16 = self.MaterialHandling(True,2,2,self.W, 3,self.buildBedVelocity, 0,0)
        self.makeStep(defaultStep,step16,"step 16 raise build bed")

        #step 17 raise feed bed
        step17 = self.MaterialHandling(True,2,2,self.W, self.FeedBedSel,self.feedBedVelocity, 0,0)
        self.makeStep(defaultStep,step17,"step 17 raise feed bed")

    def makeStep(self, default_step, Command,Comment = ""):
        NameNode = Command.find("Name")
        Name = NameNode.text

        newStep = deepcopy(default_step)
        count = int(self.XMLRoot.find("Dimsize").text)

        if(Name == "Gantry"):
            newStep[2] = Command
        elif(Name == "Z Axis"):
            newStep[3] = Command
        elif(Name == "Material Handling"):
            newStep[4] = Command
        elif(Name == "Syringe"):
            newStep[5] = Command
        elif(Name == "Printhead"):
            newStep[6]= Command
        elif(Name == "Roller"):
            newStep[7] = Command
        elif (Name == "Syringe 2"):
            newStep[8] = Command
        elif(Name == "Printhead 2"):
            newStep[9] = Command
        else:
            return None

        if(Comment):
            tagComment = etree.Comment(Comment)
        else:
            tagComment = etree.Comment("activate : {}".format(Name))
        #add comment
        self.XMLRoot.append(tagComment)
        self.XMLRoot.append(newStep)
        count = int(self.XMLRoot.find("Dimsize").text)
        count = count + 1
        self.XMLRoot.find("Dimsize").text = str(count)

        return count

    def create_default_Step(self):
        default_gantry_cluster = self.Gantry()
        default_zaxis_cluster = self.ZAxis()
        default_Material_Handling_cluster = self.MaterialHandling()
        default_Syringe_Cluster = self.Syringe()
        default_XAAR_Printhead_Cluster = self.XaarPrinthead()
        default_Roller_Cluster = self.Roller()
        default_Syringe2_Cluster = self.Syringe2()
        default_Imtech_Cluster = self.ImtechPrintHead()

        step = self.step(default_gantry_cluster,default_zaxis_cluster,
                         default_Material_Handling_cluster,default_Syringe_Cluster,
                         default_XAAR_Printhead_Cluster,default_Roller_Cluster,
                         default_Syringe2_Cluster,default_Imtech_Cluster)
        return step

    def step(self,GantryXML,ZAxisXML,MatHandlingXML,SyringeXML,XaarXML,RollerXML,Syringe2XML,ImtechXML):
        root = self.Cluster("Cluster 4",8)
        
        listOfCluster = [GantryXML,ZAxisXML,MatHandlingXML,SyringeXML,XaarXML,RollerXML,Syringe2XML,ImtechXML]
        
        for cluster in listOfCluster:
            root.append(cluster)
        return root

    def ew(self,Name,listOfChoice,Val):
        root = etree.Element("EW")
        root.append(E.Name(Name))

        for ChoiceTxt in listOfChoice:
            root.append(E.Choice(ChoiceTxt))
        
        root.append(E.Val(str(int(Val))))

        return root

    def ewModule(self,Val):
        """Function Generates Module xml tree
        
        :param Val: Tag Value
        :type Val: Int
        :return: lxml tree
        :rtype: etree.Element
        """

        listOfChoice = ["Gantry Axis","Z Axis","Material Handling Axes","Porogen Insertion",
                        "Syringe Injection","Printhead","Roller","Syringe 2","Printhead 2"]
        return self.ew("Module",listOfChoice,Val)
    
    def ewXaarFunction(self,Val):
        listOfChoice = ["Start Stop Print"]

        return self.ew("Function",listOfChoice,Val)
    
    def ewPrintMatHandlingFunction(self,Val):
        listOfChoice = ["Home","Jog","Move Height","Move Carriage to Feed Bed"]
        return self.ew("Function",listOfChoice,Val)

    def ewImtechFunction(self,Val):
        listOfChoice = ["Initialize","Load Image","Set Default Buffer","Switch VPP",
                        "Printhead Parameters","Print Now","Restart Imprint"]
        return self.ew("Function",listOfChoice,Val)
    
    def ewSyringeFunction(self,Val):
        listOfChoice = ["Initialize","Syringe Control","Extrusion ON/OFF","Kill Syringe Motor"]
        return self.ew("Function",listOfChoice,Val)
    
    def ewSyringe2Function(self,Val):
        listOfChoice = ["Initialize","Syringe Control", "Set Pressure","Set Vacuum"]
        return self.ew("Function",listOfChoice,Val)
    
    def ewMotorZ(self,Val):
        listOfChoice = ["Z1","Z2"]
        return self.ew("Z Motor",listOfChoice,Val)
    
    def ewGantryFunction(self,Val):
        listOfChoice = ["Home","Jog","Run Program","Move to Coordinates"]
        return self.ew("Function",listOfChoice,Val)
    
    def ewRollerFunction(self,Val):
        listOfChoice = ["Initialize","Set Roller Velocity","Sweep X Axis"]
        return self.ew("Function",listOfChoice,Val)
    
    def ewGantryMotorFunction(self,Val):
        listOfChoice = ["X1","X2","Y"]
        return self.ew("Motor",listOfChoice,Val)
    
    def ewZAxisFunction(self,Val):
        listOfChoice = ["Home","Jog","Move to Coordinates"]
        return self.ew("Function",listOfChoice,Val)
    
    def ewEquation(self,Val):
        listOfChoice = ["Use Height","H + T + S","H - T","-(H  + W)","+W"]
        return self.ew("Equation",listOfChoice,Val)
    
    def ewMotionControl(self,Val):
        listOfChoice = ["Incremental","Absolute","Continuous"]
        return self.ew("Motion Control",listOfChoice,Val)
    
    def ewBedSelection(self,Val):
        listOfChoice = ["Feed Bed 1","Feed Bed 2","Feed Bed 3","Build Bed","Material Box Carriage"]
        return self.ew("Bed Selection",listOfChoice,Val)

    def Cluster(self,Name,NumElts):

        root = (E.Cluster(
                    E.Name(Name),
                    E.NumElts(str(int(NumElts)))
                )
            )
            
        return root
    
    def _TypeNameVal(self,type,Name,Val):
        
        root = etree.Element(type)
        root.append(E.Name(Name))
        root.append(E.Val(str(Val)))

        return root

    def Boolean(self,Name,Val):
        return self._TypeNameVal("Boolean",Name,int(Val))
    
    def DBL(self,Name,Val):
        return self._TypeNameVal("DBL",Name,float(Val))
    
    def I16(self,Name,Val):
        return self._TypeNameVal("I16",Name,int(Val))
    
    def Path(self,Name,Val):
        return self._TypeNameVal("Path", Name,Val)
    
    def String(self,Name,Val):
        return self._TypeNameVal("String", Name,Val)

    def XaarPrinthead(self,Bool_Xaar=False,Module=0,Function=0,Img_Path=0,Start_Stop_Print=0):
        root = self.Cluster("Printhead",4)
        root.append(self.Boolean("Printhead",Bool_Xaar))

        root.append(self.ewModule(Module))
        root.append(self.ewXaarFunction(Function))

        xaarConfig = self.Cluster("Print Head Config",2)
        root.append(xaarConfig)

        xaarConfig.append(self.Path("Image File",Img_Path))
        xaarConfig.append(self.Boolean("Start Stop Print", Start_Stop_Print))

        return root
        
    def ImtechPrintHead(self,Bool_Imtech=False,Module=0,Function=0,Voltage=0,pulse_width=0,Buffer_Number=0, VPP_On_Off=0,Imtech_txtStr=0,PrintHeadAddr=0, img_path=""):
        root = self.Cluster("Printhead 2",4)
        
        root.append(self.Boolean("Imtech Printer",Bool_Imtech))
        root.append(self.ewModule(Module))

        root.append(self.ewImtechFunction(Function))

        ImtechConfig = self.Cluster("Imtech 610 Config",7)
        ImtechConfig.append(self.DBL("Vpp Voltage (V)",Voltage))
        ImtechConfig.append(self.DBL("Pulse Width (ms)",pulse_width))
        ImtechConfig.append(self.I16("Buffer Number",Buffer_Number))
        ImtechConfig.append(self.Boolean("Vpp On/Off",VPP_On_Off))
        ImtechConfig.append(self.String("Text to Print",Imtech_txtStr))
        ImtechConfig.append(self.I16("Printhead Address",PrintHeadAddr))
        ImtechConfig.append(self.Path("Image Path",img_path))

        root.append(ImtechConfig)
        return root
    
    def Syringe(self,Bool_Syringe=False,Module=0,Function=0,Bool_Extrusion=0,Syringe_Velocity=0):
        root = self.Cluster("Syringe",4)
        root.append(self.Boolean("Syringe",Bool_Syringe))

        root.append(self.ewModule(Module))
        root.append(self.ewSyringeFunction(Function))

        syringeConfig = self.Cluster("Syringe Config",2)
        syringeConfig.append(self.Boolean("Extrusion ON/OFF",Bool_Extrusion))
        syringeConfig.append(self.DBL("Syringe Velocity",Syringe_Velocity))

        root.append(syringeConfig)

        return root
    
    def Syringe2(self,Bool_Syringe=False, Module=0,Function=0,Pressure_Units=0,Pressure=0,Vacuum_Units=0,Vacuum=0,Start_Stop=0):
        root = self.Cluster("Syringe 2",4)
        root.append(self.Boolean("Syringe 2",Bool_Syringe))

        root.append(self.ewModule(Module))
        root.append(self.ewSyringe2Function(Function))

        syringe2Config = self.Cluster("Syringe Config",5)
        root.append(syringe2Config)

        syringe2Config.append(self.I16("Pressure Units",Pressure_Units))
        syringe2Config.append(self.DBL("Pressure",Pressure))
        syringe2Config.append(self.I16("Vacuum Units",Vacuum_Units))
        syringe2Config.append(self.DBL("Vacuum",Vacuum))
        syringe2Config.append(self.Boolean("Start/Stop",Start_Stop))
        
        return root

    def Gantry(self, Bool_Gantry=False, Module=0,Function=0,XYCoord=[0,0],Motor=0,MotorVelocity=0,file_path="FilePath"):

        root = self.Cluster("Gantry",4)

        root.append(self.Boolean("Gantry",Bool_Gantry))
        root.append(self.ewModule(Module))

        root.append(self.ewGantryFunction(Function))

        gantryConfigCluster = self.Cluster("Gantry Config",5)
        root.append(gantryConfigCluster)

        gantryConfigCluster.append(self.DBL("X Coordinate",XYCoord[0]))
        gantryConfigCluster.append(self.DBL("Y Coordinate",XYCoord[1]))
        gantryConfigCluster.append(self.ewGantryMotorFunction(Motor))
        gantryConfigCluster.append(self.DBL("Motor Velocity",MotorVelocity))
        gantryConfigCluster.append(self.Path("Down Load File Path",file_path))

        return root
    
    def Roller(self,Bool_Roller=False,Module=0,Function=0,Roller_Velocity=0):
        root = self.Cluster("Roller",4)
        root.append(self.Boolean("Roller",Bool_Roller))

        root.append(self.ewModule(Module))
        root.append(self.ewRollerFunction(Function))
        
        rollerConfig = self.Cluster("Roller Config",1)
        rollerConfig.append(self.DBL("Roller Velocity",Roller_Velocity))

        root.append(rollerConfig)

        return root

    def MaterialHandling(self,Bool_Mat=False, Module=0,Function=0,Height=0,Bed_Selection=0,Motor_Velocity=0,Motion_Control=0, Equation=0):
        root = self.Cluster("Material Handling",4)
        root.append(self.Boolean("Material Handling",Bool_Mat))

        root.append(self.ewModule(Module))
        root.append(self.ewPrintMatHandlingFunction(Function))

        MaterialHandlingConfig = self.Cluster("Material Handling Config",5)
        root.append(MaterialHandlingConfig)

        MaterialHandlingConfig.append(self.DBL("Height",Height))
        MaterialHandlingConfig.append(self.ewBedSelection(Bed_Selection))
        MaterialHandlingConfig.append(self.DBL("Motor Velocity",Motor_Velocity))
        MaterialHandlingConfig.append(self.ewMotionControl(Motion_Control))
        MaterialHandlingConfig.append(self.ewEquation(Equation))

        return root
    
    def ZAxis(self,Bool_ZAxis = False , Module = 0, Function = 0, Z_Coord = 0, Motor_Selection = 0, Motor_Velocity = 0):

        root = self.Cluster("Z Axis",4)
        root.append(self.Boolean("Z Axis",Bool_ZAxis))

        root.append(self.ewModule(Module))
        root.append(self.ewZAxisFunction(Function))

        Z_config_cluster = self.Cluster("Z Axis Config",3)
        root.append(Z_config_cluster)

        Z_config_cluster.append(self.DBL("Z Coordinate",Z_Coord))
        Z_config_cluster.append(self.ewMotorZ(Motor_Selection))
        Z_config_cluster.append(self.DBL("Motor Velocity",Motor_Velocity))

        return root    
        