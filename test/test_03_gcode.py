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
        if(not os.path.isdir('./test/testOutput')):
            os.mkdir('./test/testOutput')
        
        if(not os.path.isdir(self.OutputFolder)):
            os.mkdir(self.OutputFolder)
        else:
            shutil.rmtree(self.OutputFolder)
            os.mkdir(self.OutputFolder)

        os.mkdir(self.testConfigFolder)
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
        self.stlActor.RotateZ(45) 
    
    def test_generategcode(self):
        
        blackSlicer = FullBlackImageSlicer(self.test_config)
        blackSlicer.addActor(self.stlActor)
        BuildVtkImage = blackSlicer.slice()

        gcodewriter = gcodeWriterVlaseaBM(self.test_config,self.OutputFolder)
        gcodewriter.SetInput(blackSlicer)
        gcodewriter.generateGCode()
        

    def tearDown(self):
        shutil.rmtree(self.testConfigFolder)