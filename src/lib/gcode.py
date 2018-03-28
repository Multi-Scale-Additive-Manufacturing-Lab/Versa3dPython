import vtk
from src.lib.versa3dConfig import config
from lxml import etree
from lxml.builder import E

def gcodeFactory(type, config):
    
    if('VlaseaBM' == type):
        return gcodeWriterVlaseaBM(config)
    else:
        return None


class gcodeWriter():
    def __init__(self,config):
        self._config =config
    
    def generateGCode(self,BuildBedVTKImage):
        pass

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

        self._Module_Dict = {"Gantry_axis":0, "Z_Axis":1,
                            "Material_Handling_Axis":2 , "Porogen_Insertion":3,
                            "Syringe_Injection":4,"Printhead":5,
                            "Roller":6, "Syringe_2":7,"Printhead_2":8}
        
        self._Function_Dict = {"Init":0,"txt_to_print":1,
                                "Set_Default_Buffer":2,"Switch_vpp":3,
                                "Printhead_param":4,"Print_Now":5}

    def SetInput(self,slicer):
        """Set Input slicer
        
        :param slicer: slicer class
        :type slicer: VoxelSlicer object
        """
        self._Slicer = slicer   

    def generateGCode(self):
        bmpWriter = vtk.vtkBMPWriter()
        BuildVtkImage = self._Slicer.getBuildVolume()
        (xDim,yDim,zDim) = BuildVtkImage.GetDimensions()
        
        imageFolder = os.path.join(self._Folderpath,"Image")
        os.mkdir(imageFolder)

        for z in range(0,zDim):
            fileName = "slice_"+str(z)+".bmp"
            FullPath = os.path.join(imageFolder,fileName)
            bmpWriter.SetFileName(FullPath)
            slicer = vtk.vtkExtractVOI()
            slicer.SetVOI(0,xDim-1,0,yDim-1,z,z)
            slicer.SetSampleRate(1,1,1)
            slicer.SetInputData(BuildVtkImage)
            slicer.Update()

            if (z <= self._Slicer.getCeiling()):
                bmpWriter.SetInputData(slicer.GetOutput())
                bmpWriter.Write()
                self.generateGCodeLayer(FullPath)
    
    def generateGCodeLayer(self,imgPath):
        
        pass
        
    def step(self,GantryXML,ZAxisXML,MatHandlingXML,SyringeXML,XaarXML,RollerXML,Syringe2XML,ImtechXML):
        root = etree.Element("Cluster 4",8)
        
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
    
    def ewGantryMotor(self,Val):
        listOfChoice = ["X1","X2","Y"]
        return self.ew("Motor",listOfChoice,Val)
    
    def ewZAxis(self,Val):
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

    def XaarPrinthead(self,Bool_Xaar,Module,Function,Img_Path,Start_Stop_Print):
        root = self.Cluster("Printhead",4)
        root.append(self.Boolean("Printhead",Bool_Xaar))

        root.append(self.ewModule(Module))
        root.append(self.ewXaarFunction(Function))

        xaarConfig = self.Cluster("Print head Config",2)
        root.append(xaarConfig)

        xaarConfig.append(self.Path(Img_Path))
        xaarConfig.append(self.Boolean("Start Stop Print", Start_Stop_Print))

        return root
        
    def ImtechPrintHead(self,Bool_Imtech,Module,Function,Voltage,pulse_width,Buffer_Number, VPP_On_Off,Imtech_txtStr,PrintHeadAddr, img_path):
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
    
    def Syringe(self,Bool_Syringe,Module,Function,Bool_Extrusion,Syringe_Velocity):
        root = self.Cluster("Syringe",4)
        root.append(self.Boolean("Syringe",Bool_Syringe))

        root.append(self.ewModule(Module))
        root.append(self.ewSyringeFunction(Function))

        syringeConfig = self.Cluster("Syringe Config",2)
        syringeConfig.append(self.Boolean("Extrusion ON/OFF",Bool_Extrusion))
        syringeConfig.append(self.DBL("Syringe",Syringe_Velocity))

        root.append(syringeConfig)

        return root
    
    def Syringe2(self,Bool_Syringe, Module,Function,Pressure_Units,Pressure,Vacuum_Units,Vacuum,Start_Stop):
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

    def Gantry(self, Bool_Gantry, Module,Function,XYCoord,Motor,MotorVelocity,file_path):

        root = self.Cluster("Gantry",4)

        root.append(self.Boolean("Gantry",Bool_Gantry))
        root.append(self.ewModule(Module))

        root.append(self.ewGantryFunction(Function))

        gantryConfigCluster = self.Cluster("Gantry Config",5)
        root.append(gantryConfigCluster)

        gantryConfigCluster.append(self.DBL("X Coordinate",XYCoord[0]))
        gantryConfigCluster.append(self.DBL("Y Coordinate",XYCoord[1]))
        gantryConfigCluster.append(self.ewGantryMotor(Motor))
        gantryConfigCluster.append(self.DBL("Motor Velocity",MotorVelocity))
        gantryConfigCluster.append(self.Path("Down Load File Path",file_path))

        return root
    
    def Roller(self,Bool_Roller,Module,Function,Roller_Velocity):
        root = self.Cluster("Roller",4)
        root.append(self.Boolean("Roller",Bool_Roller))

        root.append(self.ewModule(Module))
        root.append(self.ewRollerFunction(Function))
        
        rollerConfig = self.Cluster("Roller Config",1)
        rollerConfig.append(self.DBL("Roller Velocity",Roller_Velocity))

        root.append(rollerConfig)

        return root

    def MaterialHandling(self,Bool_Mat, Module,Function,Height,Bed_Selection,Motor_Velocity,Motion_Control, Equation):
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
    
        

        