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

    
    def test_slicerFactory(self):
        AllBlackSlicer = slicerFactory('black',self.test_config)
        self.assertEqual(FullBlackImageSlicer, type(AllBlackSlicer))

        NullCase = slicerFactory(None,None)
        self.assertEqual(None,NullCase)

    def test_blackSlicing(self):
        
        blackSlicer = FullBlackImageSlicer(self.test_config)
        blackSlicer.addActor(self.stlActor)
        BuildVtkImage = blackSlicer.slice()

        vtkImageStat  = vtk.vtkImageHistogram()
        vtkImageStat.AutomaticBinningOn()
        vtkImageStat.SetInputData(BuildVtkImage)
        vtkImageStat.Update()

        stats = vtkImageStat.GetHistogram()
        BlackNum = stats.GetValue(0)
        WhiteNum = stats.GetValue(255)
        
        totalVoxel = vtkImageStat.GetTotal()
        
        BuildBedSize = self.test_config.getMachineSetting('printbedsize')
        dpi = self.test_config.getPrintHeadSetting('dpi')
        thickness = self.test_config.getSlicingSetting('layer_thickness')
        BuildHeight = self.test_config.getMachineSetting('buildheight')

        BuildBedVoxSize = [0]*3
        for i in range(0,2):
            BuildBedVoxSize[i]=int(math.ceil(BuildBedSize[i]*dpi[i]/(0.0254*1000)))

        BuildBedVoxSize[2] = math.ceil(BuildHeight/thickness)

        theoreticalNumberOfVoxel = BuildBedVoxSize[0]*BuildBedVoxSize[1]*BuildBedVoxSize[2]
        #check number of voxel
        self.assertEqual(theoreticalNumberOfVoxel,totalVoxel)
        #check blackness
        self.assertLessEqual(0.02,BlackNum/totalVoxel)

        #uncomment if you want to visual check
        
        Renderer = vtk.vtkRenderer()
        RendererWindow = vtk.vtkRenderWindow()
        RendererWindow.AddRenderer(Renderer)

        (xMin,xMax,yMin,yMax,zMin,zMax) = BuildVtkImage.GetExtent()

        voxelSurface = vtk.vtkContourFilter()
        voxelSurface.SetInputData(BuildVtkImage)
        voxelSurface.SetValue(0,254.99)

        voxelMapper = vtk.vtkPolyDataMapper()
        voxelMapper.SetInputConnection(voxelSurface.GetOutputPort())

        voxelActor = vtk.vtkActor()
        voxelActor.SetMapper(voxelMapper)
        Renderer.AddActor(voxelActor)

        Renderer.ResetCamera()

        Interactor = vtk.vtkRenderWindowInteractor()
        #Interactor.SetInteractorStyle(vtk.vtkInteractorStyleImage())
        Interactor.SetRenderWindow(RendererWindow)
        Interactor.Initialize()
        RendererWindow.Render()
        Interactor.Start()

    def tearDown(self):
        shutil.rmtree(self.testFileFolder)