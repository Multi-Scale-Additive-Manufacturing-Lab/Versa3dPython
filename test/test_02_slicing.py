import unittest
import vtk
import re
import os
import fnmatch
import shutil
import math
from src.lib.slicing import slicerFactory, FullBlackImageSlicer,CheckerBoardImageSlicer , VoxelSlicer
from src.lib.versa3dConfig import config

class TestSlicer(unittest.TestCase):

    def setUp(self):
        reader = vtk.vtkSTLReader()
        reader.SetFileName('./test/testFile/3DBenchySmall.stl')
        reader.Update()

        self.testFileFolder = './configtest'
        os.mkdir(self.testFileFolder)
        self.test_config = config(self.testFileFolder)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        mapper2 = vtk.vtkPolyDataMapper()
        polydata = vtk.vtkPolyData()
        polydata.DeepCopy(reader.GetOutput())
        mapper2.SetInputData(polydata)

        self.stlActor = vtk.vtkActor()
        self.stlActor.SetMapper(mapper)

        self.stlActor2 = vtk.vtkActor()
        self.stlActor2.SetMapper(mapper2)

        printBedSize = self.test_config.getMachineSetting("printbedsize")
        zRange = self.stlActor.GetZRange()

        newPosition = [0]*3

        oldPosition = self.stlActor.GetPosition()
        newPosition[0] = printBedSize[0]/4
        newPosition[1] = printBedSize[1]/4

        if(zRange[0]<0):
            newPosition[2] = oldPosition[2]-zRange[0]
        else:
            newPosition[2] = oldPosition[2]
        
        self.stlActor.SetPosition(newPosition)
        self.stlActor2.SetPosition(newPosition[0]*2,newPosition[1]*3,newPosition[2])

    def test_slicerFactory(self):
        AllBlackSlicer = slicerFactory(self.test_config)
        self.assertEqual(FullBlackImageSlicer, type(AllBlackSlicer))

        NullCase = slicerFactory(None)
        self.assertEqual(None,NullCase)

    def test_blackSlicing(self):
        
        blackSlicer = FullBlackImageSlicer(self.test_config)

        blackSlicer.addActor(self.stlActor)
        blackSlicer.addActor(self.stlActor2)

        BuildVtkImage = blackSlicer.slice()

        #vtkImageStat  = vtk.vtkImageHistogram()
        #vtkImageStat.AutomaticBinningOn()
        #vtkImageStat.SetInputData(BuildVtkImage)
        #vtkImageStat.Update()

        #stats = vtkImageStat.GetHistogram()
        #BlackNum = stats.GetValue(0)
        #WhiteNum = stats.GetValue(255)
        
        #totalVoxel = vtkImageStat.GetTotal()
        
        BuildBedSize = self.test_config.getMachineSetting('printbedsize')
        dpi = self.test_config.getPrintHeadSetting('dpi')
        thickness = self.test_config.getPrintSetting('layer_thickness')
        BuildHeight = self.test_config.getMachineSetting('buildheight')

        BuildBedVoxSize = [0]*3
        for i in range(0,2):
            BuildBedVoxSize[i]=int(math.ceil(BuildBedSize[i]*dpi[i]/(0.0254*1000)))

        BuildBedVoxSize[2] = math.ceil(BuildHeight/thickness)

        bmpWriter = vtk.vtkBMPWriter()
        folderPath = './test/testOutput/FullBlack'

        if(not os.path.isdir(folderPath)):
            os.mkdir(folderPath)
        else:
            shutil.rmtree(folderPath)
            os.mkdir(folderPath)

        count = 0
        for image in BuildVtkImage:

            imgFullPath = os.path.join(folderPath,'img_%d.bmp'%(count))
            bmpWriter.SetFileName(imgFullPath)
            bmpWriter.SetInputData(image.getImage())
            count = count +1
            bmpWriter.Write()

        #theoreticalNumberOfVoxel = BuildBedVoxSize[0]*BuildBedVoxSize[1]*BuildBedVoxSize[2]
        #check number of voxel
        #self.assertEqual(theoreticalNumberOfVoxel,totalVoxel)
        #check blackness
        #self.assertLessEqual(0.02,BlackNum/totalVoxel)

        #uncomment if you want to visual check
        

    def tearDown(self):
        shutil.rmtree(self.testFileFolder)