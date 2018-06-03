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
        self.ListActor = []
        #generate cylinder aligned z axis
        for i in range(0,2):
            for j in range(0,2):
                axis = vtk.vtkLineSource()
                axis.SetPoint1(10.0*i+10.0,10.0*j+10.0,0.0)
                axis.SetPoint2(10.0*i+10.0,10.0*j+10.0,10.0)

                tube = vtk.vtkTubeFilter()
                tube.SetInputConnection(axis.GetOutputPort())
                tube.SetRadius(5.0)
                tube.SetNumberOfSides(100)
                tube.CappingOn()
                tube.Update()

                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputConnection(tube.GetOutputPort())

                tubeActor = vtk.vtkActor()
                tubeActor.SetMapper(mapper)
                self.ListActor.append(tubeActor)
                

        printBedSize = self.test_config.getMachineSetting("printbedsize")
    
    def test_generategcode(self):
        
        blackSlicer = FullBlackImageSlicer(self.test_config)

        for actor in self.ListActor:
            blackSlicer.addActor(actor)

        BuildVtkImage = blackSlicer.slice()

        gcodewriter = gcodeWriterVlaseaBM(self.test_config,self.OutputFolder)
        gcodewriter.SetInput(blackSlicer)
        gcodewriter.generateGCode()
        

    def tearDown(self):
        shutil.rmtree(self.testConfigFolder)