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
    
    def ewModule(self,Val):
        root = (E.EW(
                    E.Name("Module"),
                    E.Choice("Gantry Axis"),
                    E.Choice("Z Axis"),
                    E.Choice("Material Handling Axes"),
                    E.Choice("Porogen Insertion"),
                    E.Choice("Syringe Injection"),
                    E.Choice("Printhead"),
                    E.Choice("Roller"),
                    E.Choice("Syringe 2"),
                    E.Choice("Printhead 2"),
                    E.Val(str(Val))
                )
            )

        return page
    
    def ewFunction(self,Val):

        root = ( E.EW(
                    E.Name("Function"),
                    E.Choice("Initialise"),
                    E.Choice("Text to Print"),
                    E.Choice("Set Default Buffer"),
                    E.Choice("Switch VPP"),
                    E.Choice("Printhead Parameters"),
                    E.Choice("Print Now"),
                    E.Val(str(Val))
                )
            )
        
        return root

    def cluster(self,Name,NumElts):

        root = (E.Cluster(
                    E.Name(Name),
                    E.NumElts(NumElts)
                )
            )
            
        return root

    def PrintHeadSetUp(self,Bool_Imtech_Printer,Module,Function,Voltage,pulse_width,Buffer_Number, VPP_On_Off,Imtech_txtStr,PrintHeadAddr, img_path):
        root = etree.parse("./src/lib/gcode_template/printHeadCluster.xml")

        root.find("/Boolean/Val").text = str(Bool_Imtech_Printer)

        EWElems = root.findall("EW")
        EWElems[0].find("Val").text = str(Module)
        EWElems[1].find("Val").text = str(Function)

        DBLElemList = root.findall("//DBL")
        DBLElemList[0].find("Val").text = str(Voltage)
        DBLElemList[1].find("Val").text = str(pulse_width)
        
        I16ElemList = root.findall("//I16")
        I16ElemList[0].find("Val").text = str(Buffer_Number)
        I16ElemList[1].find("Val").text = str(PrintHeadAddr)

        root.find("/Cluster/Boolean/Val").text = str(VPP_On_Off)
        root.find("/Cluster/String/Val").text = Imtech_txtStr
        root.find("/Cluster/Path/Val").text = img_path
        
        return root

        

        