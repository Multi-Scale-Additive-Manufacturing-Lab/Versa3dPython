import vtk
from src.lib.versa3dConfig import config
from lxml import etree
from lxml.builder import E
from copy import deepcopy
import math
import os
import string

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
        self.AbsPathBMVlaseaComputer = config.getVersa3dSetting('imgbmvlasealocalpath')
        
        self.dpi = config.getPrintHeadSetting('dpi')

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
            (xDim, yDim,zDim) = OriginalImg.GetDimensions()

            NumSubImage = math.ceil(yDim/self.XImageSizeLimit)
            origin = list(OriginalImg.GetOrigin())

            OffsetRealCoord = (150.0/self.dpi[0])*25.4

            yStart = 0
            listOfImg = []
            for i in range(0, NumSubImage):
                yEnd = yStart+self.XImageSizeLimit

                if (yDim-1) < yEnd:
                    yEnd = yDim-1

                slicer = vtk.vtkExtractVOI()
                slicer.SetVOI(0,xDim-1,yStart,yEnd,0,0)
                slicer.SetSampleRate(1,1,1)
                slicer.SetInputData(OriginalImg)
                slicer.Update()

                slicedImg = slicer.GetOutput()
                origin[2] = origin[2]+OffsetRealCoord
                slicedImg.SetOrigin(origin)

                listOfImg.append(slicedImg)
                yStart = yEnd+1

            self.XMLRoot = self.BuildSequenceCluster(0)

            self.generateGCodeLayer(count,listOfImg,imageFolder)

            xmlFileName = "layer_%d.xml"%(count)
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
    
    def generateGCodeLayer(self,layerNum,imgSliceList,imageFolder):

        defaultStep = self.create_default_Step()
        BNumber = 0
        listOfAlphabet = list(string.ascii_uppercase)
        fontNumber = 1
        listTxtToPrint = []
        listOfXCoord = []

        count = 0
        for individualSlice in imgSliceList:

            imageStat = vtk.vtkImageHistogram()
            imageStat.AutomaticBinningOn()
            imageStat.SetInputData(individualSlice)
            imageStat.Update()

            origin = individualSlice.GetOrigin()
            dimension = individualSlice.GetDimensions()
            spacing = individualSlice.GetSpacing()

            totalpixel = imageStat.GetTotal()
            results = imageStat.GetHistogram()
            
            numberOfBlackPixel = results.GetValue(0)

            if(numberOfBlackPixel != 0):
                bmpWriter = vtk.vtkBMPWriter()

                imgfileName = "slice_{0:d}_{1:d}.bmp".format(layerNum,count)

                if(self.AbsPathBMVlaseaComputer):
                    baseFolder = "C:\Documents and Settings\Administrator\Desktop\InputVersa3d\{}\image\\".format(os.path.basename(self._Folderpath))
                    imgPath = baseFolder+imgfileName
                else:
                    baseFolder = os.path.join("./","image")
                    imgPath = os.path.join(baseFolder,imgfileName)

                imgFullPath = os.path.join(imageFolder,imgfileName)
                bmpWriter.SetFileName(imgFullPath)
                bmpWriter.SetInputData(individualSlice)
                bmpWriter.Write()

                #step 0 - turn ON printhead and get ready to print buffer 0
                textStr = "%T"+str(fontNumber).zfill(2)+listOfAlphabet[fontNumber-1]
                step0 = self.ImtechPrintHead(1,8,1,0,0,BNumber,0,textStr,self.DefaultPrintHeadAddr,imgPath)
                self.makeStep(defaultStep,step0)
                BNumber = BNumber + 1
                fontNumber = fontNumber + 1
                listTxtToPrint.append(textStr)

            count = count + 1

            listOfXCoord.append(10*count+10)

        #step 1 - move gantry to X1 = 0 
        step1 = self.Gantry(1,0,3,[0,0],0,self.gantryXYVelocity[0],"")
        self.makeStep(defaultStep,step1)

        #step 2 - move to Y = 0
        step2 = self.Gantry(1,0,3,[0,0],2,self.gantryXYVelocity[1],"")
        self.makeStep(defaultStep,step2)

        #step 3 - turn on roller
        step3 = self.Roller(1,6,1,self.rollerRotVel)
        self.makeStep(defaultStep,step3)
        
        #step 4 - material handling raise feed bed by = H+T+S
        step4 = self.MaterialHandling(1,2,2,self.H+self.Thickness+self.S,self.FeedBedSel,self.feedBedVelocity,0,0)
        self.makeStep(defaultStep,step4)

        #step 5 - material handling raise build bed by = H-T
        step5 = self.MaterialHandling(1,2,2,self.H-self.Thickness,self.FeedBedSel,self.feedBedVelocity,0,0)
        self.makeStep(defaultStep,step5)

        #step 6 - spread the powder by moving in X-coordinate 300
        step6 = self.Gantry(1,0,3,[300,0],0,self.rollerLinVel,"")
        self.makeStep(defaultStep,step6)

        #step 7 - turn off roller
        step7 = self.Roller(1,6,1,0)
        self.makeStep(defaultStep,step7)

        #step 8 - lower build bed by -(H+W)
        step8 = self.MaterialHandling(1,2,2,(-2)*(self.H+self.W),3, self.buildBedVelocity,0,0)
        self.makeStep(defaultStep,step8)

        for i in range(0,BNumber):

            #step 9 allign printhead with the printing area - move to lower left corner of image
            step9 = self.Gantry(1,0,3,[0,58-origin[0]],2,self.gantryXYVelocity[1],"")
            self.makeStep(defaultStep,step9)

            #step 10 allign printhead with the printing area - move to X=10
            step10 = self.Gantry(1,0,3,[20-origin[1],0],0,self.gantryXYVelocity[0],"")
            self.makeStep(defaultStep,step10)

            #step 11 turn ON printhead and get ready to print buffer 0
            step11 = self.ImtechPrintHead(1,8,5,0,0,i,0,listTxtToPrint[i],self.DefaultPrintHeadAddr)
            self.makeStep(defaultStep,step11)

            #step 12 execute printing motion in Y direction - move to right
            step12 = self.Gantry(1,0,3,[0,38],2,self.DefaultPrintVelocity,"")
            self.makeStep(defaultStep,step12)
        
        #step 13 move back to origin in Y -direction Y=0(former step 16)
        step13 = self.Gantry(1,0,3,[0,0],2,self.gantryXYVelocity[1],"")
        self.makeStep(defaultStep,step13)

        #step 14 move back to origin in X-direction X=0 (former stp 18)
        step14 = self.Gantry(1,0,3,[0,0],0,self.gantryXYVelocity[0],"")
        self.makeStep(defaultStep,step14)
        
        #step 15 raise build bed
        step15 = self.MaterialHandling(1,2,2,2*self.W, 3,self.buildBedVelocity, 0,0)
        self.makeStep(defaultStep,step15)


    
    def makeStep(self, default_step, Command):
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
        
        root.append(E.Val(str(Val)))

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
        listOfChoice = ["Use Height","H + T + S","H - T","-(H + W)","+W"]
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
                    E.NumElts(str(NumElts))
                )
            )
            
        return root
    
    def _TypeNameVal(self,type,Name,Val):
        
        root = etree.Element(type)
        root.append(E.Name(Name))
        root.append(E.Val(str(Val)))

        return root

    def Boolean(self,Name,Val):
        return self._TypeNameVal("Boolean",Name,Val)
    
    def DBL(self,Name,Val):
        return self._TypeNameVal("DBL",Name,Val)
    
    def I16(self,Name,Val):
        return self._TypeNameVal("I16",Name,Val)
    
    def Path(self,Name,Val):
        return self._TypeNameVal("Path", Name,Val)
    
    def String(self,Name,Val):
        return self._TypeNameVal("String", Name,Val)

    def XaarPrinthead(self,Bool_Xaar=0,Module=0,Function=0,Img_Path="",Start_Stop_Print=0):
        root = self.Cluster("Printhead",4)
        root.append(self.Boolean("Printhead",Bool_Xaar))

        root.append(self.ewModule(Module))
        root.append(self.ewXaarFunction(Function))

        xaarConfig = self.Cluster("Print head Config",2)
        root.append(xaarConfig)

        xaarConfig.append(self.Path("Image File",Img_Path))
        xaarConfig.append(self.Boolean("Start Stop Print", Start_Stop_Print))

        return root
        
    def ImtechPrintHead(self,Bool_Imtech=0,Module=0,Function=0,Voltage=0,pulse_width=0,Buffer_Number=0, VPP_On_Off=0,Imtech_txtStr=0,PrintHeadAddr=0, img_path=""):
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
    
    def Syringe(self,Bool_Syringe=0,Module=0,Function=0,Bool_Extrusion=0,Syringe_Velocity=0):
        root = self.Cluster("Syringe",4)
        root.append(self.Boolean("Syringe",Bool_Syringe))

        root.append(self.ewModule(Module))
        root.append(self.ewSyringeFunction(Function))

        syringeConfig = self.Cluster("Syringe Config",2)
        syringeConfig.append(self.Boolean("Extrusion ON/OFF",Bool_Extrusion))
        syringeConfig.append(self.DBL("Syringe",Syringe_Velocity))

        root.append(syringeConfig)

        return root
    
    def Syringe2(self,Bool_Syringe=0, Module=0,Function=0,Pressure_Units=0,Pressure=0,Vacuum_Units=0,Vacuum=0,Start_Stop=0):
        root = self.Cluster("Syringe 2",2)
        root.append(self.Boolean("Syringe 2",Bool_Syringe))

        root.append(self.ewModule(Module))
        root.append(self.ewSyringe2Function(Function))

        syringe2Config = self.Cluster("Syringe 2",5)
        root.append(syringe2Config)

        syringe2Config.append(self.I16("Pressure Units",Pressure_Units))
        syringe2Config.append(self.DBL("Pressure",Pressure))
        syringe2Config.append(self.I16("Vacuum_Units",Vacuum_Units))
        syringe2Config.append(self.DBL("Vacuum",Vacuum))
        syringe2Config.append(self.Boolean("Start/Stop",Start_Stop))
        
        return root

    def Gantry(self, Bool_Gantry=0, Module=0,Function=0,XYCoord=[0,0],Motor=0,MotorVelocity=0,file_path="FilePath"):

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
    
    def Roller(self,Bool_Roller=0,Module=0,Function=0,Roller_Velocity=0):
        root = self.Cluster("Roller",4)
        root.append(self.Boolean("Roller",Bool_Roller))

        root.append(self.ewModule(Module))
        root.append(self.ewRollerFunction(Function))
        
        rollerConfig = self.Cluster("Roller Config",1)
        rollerConfig.append(self.DBL("Roller Velocity",Roller_Velocity))

        root.append(rollerConfig)

        return root

    def MaterialHandling(self,Bool_Mat=0, Module=0,Function=0,Height=0,Bed_Selection=0,Motor_Velocity=0,Motion_Control=0, Equation=0):
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
    
    def ZAxis(self,Bool_ZAxis = 0 , Module = 0, Function = 0, Z_Coord = 0, Motor_Selection = 0, Motor_Velocity = 0):

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
        