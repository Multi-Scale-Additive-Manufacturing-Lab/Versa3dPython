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

    def __init__(self,config):
        super().__init__(config)

        self._Module_Dict = {"Gantry_axis":0, "Z_Axis":1,
                            "Material_Handling_Axis":2 , "Porogen_Insertion":3,
                            "Syringe_Injection":4,"Printhead":5,
                            "Roller":6, "Syringe_2":7,"Printhead_2":8}
        
        self._Function_Dict = {"Init":0,"txt_to_print":1,
                                "Set_Default_Buffer":2,"Switch_vpp":3,
                                "Printhead_param":4,"Print_Now":5}
    def ew(self,Name,listOfChoice,Val):
        root = etree.Element("EW")
        root.append(E.Name(Name))

        for ChoiceTxt in listOfChoice:
            root.append(E.Choice(ChoiceTxt))
        
        root.append(E.Val(str(Val)))

        return root

    def ewModule(self,Val):
        listOfChoice = ["Gantry Axis","Z Axis","Material Handling Axes","Porogen Insertion",
                        "Syringe Injection","Printhead","Roller","Syringe 2","Printhead 2"]
        return self.ew("Module",listOfChoice,Val)
    
    def ewPrintHeadFunction(self,Val):
        listOfChoice = ["Initialisation","Set Roller Velocity", "Sweep X Axis"]

        return self.ew("Function",listOfChoice,Val)
    
    def ewPrintMatHandlingFunction(self,Val):
        listOfChoice = ["Home","Jog","Move Height","Move Carriage to Feed Bed"]
        return self.ew("Function",listOfChoice,Val)

    def ewPrintHead2Function(self,Val):
        listOfChoice = ["Initialise","Text to Print","Set Default Buffer","Switch VPP",
                        "Printhead Parameters","Print Now"]
        return self.ew("Function",listOfChoice,Val)
    
    def ewSyringe2Function(self,Val):
        listOfChoice = ["Initialize","Syringe Control","Set Pressure","Set Vacuum"]
        return self.ew("Function",listOfChoice,Val)
    
    def ewMotorZ(self,Val):
        listOfChoice = ["Z1","Z2"]
        return self.ew("Z Motor",listOfChoice,Val)
    
    def ewGantryFunction(self,Val):
        listOfChoice = ["Home","Jog","Run Program","Move to Coordinates"]
        return self.ew("Function",listOfChoice,Val)
    
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

    def PrintHead2SetUp(self,Bool_Imtech_Printer,Module,Function,Voltage,pulse_width,Buffer_Number, VPP_On_Off,Imtech_txtStr,PrintHeadAddr, img_path):
        root = self.Cluster("Printhead 2",4)
        
        root.append(self.Boolean("Imtech Printer",Bool_Imtech_Printer))
        root.append(self.ewModule(Module))

        root.append(self.ewPrintHead2Function(Function))

        configCluster = self.Cluster("Imtech 610 Config",7)
        configCluster.append(self.DBL("Vpp Voltage (V)",Voltage))
        configCluster.append(self.DBL("Pulse Width (ms)",pulse_width))
        configCluster.append(self.I16("Buffer Number",Buffer_Number))
        configCluster.append(self.Boolean("Vpp On/Off",VPP_On_Off))
        configCluster.append(self.String("Text to Print",Imtech_txtStr))
        configCluster.append(self.I16("Printhead Address",PrintHeadAddr))
        configCluster.append(self.Path("Image Path",img_path))

        root.append(configCluster)
        return root

        

        