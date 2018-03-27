import unittest
import os
from src.lib.versa3dConfig import config
from src.lib.gcode import gcodeWriterVlaseaBM
from lxml import etree

class gcodeTest(unittest.TestCase):

    def setUp(self):
        self.test_config = config("test.ini")

    def test_bmWriter(self):
        gcodewriter = gcodeWriterVlaseaBM(self.test_config)

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

        

    def tearDown(self):
        os.remove("test.ini")