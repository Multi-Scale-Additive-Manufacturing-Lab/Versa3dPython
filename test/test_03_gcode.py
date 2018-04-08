import unittest
import os
from src.lib.versa3dConfig import config
from src.lib.gcode import gcodeWriterVlaseaBM
from src.lib.slicing import slicerFactory,FullBlackImageSlicer,VoxelSlicer
from lxml import etree
import shutil
import vtk

class gcodeTest(unittest.TestCase):

    def setUp(self):
        self.testConfigFolder = './configtest'
        self.OutputFolder = './test/testOutput/Gcode'

        shutil.rmtree(self.OutputFolder)

        os.mkdir(self.testConfigFolder)
        os.mkdir(self.OutputFolder)
        self.test_config = config(self.testConfigFolder)

        reader = vtk.vtkSTLReader()
        reader.SetFileName('./test/testFile/3DBenchySmall.stl')
        reader.Update()

        self.stlPolyData = reader.GetOutput()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        self.stlActor = vtk.vtkActor()
        self.stlActor.SetMapper(mapper)

        printBedSize = self.test_config.getMachineSetting("printbedsize")
        zRange = self.stlActor.GetZRange()

        newPosition = [0]*3

        oldPosition = self.stlActor.GetPosition()
        newPosition[0] = printBedSize[0]/2
        newPosition[1] = printBedSize[1]/2

        if(zRange[0]<0):
            newPosition[2] = oldPosition[2]-zRange[0]
        else:
            newPosition[2] = oldPosition[2]
        
        self.stlActor.SetPosition(newPosition)

    def test_ImtechPrintHead(self):
        gcodewriter = gcodeWriterVlaseaBM(self.test_config,"test")

        default_txt_str = "T%01A"

        Bool_Imtech = 1
        Module = 8
        Function = 1
        Voltage = 0
        pulse_width = 0
        Buffer_Number = 0
        VPP_On_Off = 0
        PrintHeadAddr = 1
        Path = "./rel.png"
        resultRoot = gcodewriter.ImtechPrintHead(Bool_Imtech,Module,Function,Voltage,pulse_width,Buffer_Number,
                                            VPP_On_Off,default_txt_str,PrintHeadAddr,Path)

        ImtechElem = resultRoot.find("Boolean")
        self.assertEqual(ImtechElem.find("Val").text,str(Bool_Imtech))

        EWElemList = resultRoot.findall("EW")
        self.assertEqual(EWElemList[0].find("Val").text,str(Module))
        self.assertEqual(EWElemList[1].find("Val").text,str(Function))

        DBLElemList = resultRoot.findall(".//DBL")
        self.assertEqual(DBLElemList[0].find("Val").text,str(Voltage))
        self.assertEqual(DBLElemList[1].find("Val").text,str(pulse_width))

        I16ElemList = resultRoot.findall(".//I16")
        self.assertEqual(I16ElemList[0].find("Val").text,str(Buffer_Number))
        self.assertEqual(I16ElemList[1].find("Val").text,str(PrintHeadAddr))

        self.assertEqual(resultRoot.find("./Cluster/Boolean/Val").text, str(VPP_On_Off))

        self.assertEqual(resultRoot.find("./Cluster/String/Val").text, default_txt_str)

        self.assertEqual(resultRoot.find("./Cluster/Path/Val").text, Path)
    
    def test_generategcode(self):
        
        blackSlicer = FullBlackImageSlicer(self.test_config)
        blackSlicer.addActor(self.stlActor)
        BuildVtkImage = blackSlicer.slice()

        gcodewriter = gcodeWriterVlaseaBM(self.test_config,self.OutputFolder)
        gcodewriter.SetInput(blackSlicer)
        gcodewriter.generateGCode()
        

    def tearDown(self):
        shutil.rmtree(self.testConfigFolder)