import unittest
import vtk
import re
import os
import fnmatch
import shutil
import math
from src.lib.slicing import slicerFactory, FullBlackImageSlicer,CheckerBoardImageSlicer , VoxelSlicer
from src.lib.versa3dConfig import FillEnum , config

class TestSlicer(unittest.TestCase):

    def setUp(self):
        reader = vtk.vtkSTLReader()
        reader.SetFileName('./test/testFile/3DBenchySmall.stl')
        reader.Update()

        self.test_config = config("test.ini")

        self.stlPolyData = reader.GetOutput()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        self.stlActor = vtk.vtkActor()
        self.stlActor.SetMapper(mapper)

        printBedSize = self.test_config.getValue("printbedsize")
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
        AllBlackSlicer = slicerFactory('black')
        self.assertEqual(FullBlackImageSlicer, type(AllBlackSlicer))

        CheckBoardSlicer = slicerFactory('checker_board')
        self.assertEqual(CheckerBoardImageSlicer, type(CheckBoardSlicer))

        NullCase = slicerFactory(None)
        self.assertEqual(None,NullCase)

    def test_blackSlicing(self):
        
        blackSlicer = FullBlackImageSlicer(self.test_config)
        blackSlicer.addActor(self.stlActor)
        BuildVtkImage = blackSlicer.slice()

        vtkImageStat = vtk.vtkImageAccumulate()
        vtkImageStat.DebugOn()
        vtkImageStat.SetComponentSpacing(1,0,0)
        vtkImageStat.SetComponentExtent(0,1,0,0,0,0)
        vtkImageStat.SetComponentOrigin(0,0,0)
        vtkImageStat.SetInputData(BuildVtkImage)
        vtkImageStat.Update()
        
        totalVoxel = vtkImageStat.GetVoxelCount()
        meanArray = vtkImageStat.GetMean()
        
        BuildBedSize = self.test_config.getValue('printbedsize')
        dpi = self.test_config.getValue('dpi')
        thickness = self.test_config.getValue('layer_thickness')
        BuildHeight = self.test_config.getValue('buildheight')

        BuildBedVoxSize = [0]*3
        for i in range(0,2):
            BuildBedVoxSize[i]=int(math.ceil(BuildBedSize[i]*dpi[i]/(0.0254*1000)))

        BuildBedVoxSize[2] = math.ceil(BuildHeight/thickness)

        theoreticalNumberOfVoxel = BuildBedVoxSize[0]*BuildBedVoxSize[1]*BuildBedVoxSize[2]
        #check number of voxel
        self.assertEqual(theoreticalNumberOfVoxel,totalVoxel)
        #check blackness
        self.assertLessEqual(0.95,meanArray[0]/255)

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
        
        
    def test_BMPExport(self):

        blackSlicer = FullBlackImageSlicer(self.test_config)
        blackSlicer.addActor(self.stlActor)
        BuildVtkImage = blackSlicer.slice()

        (xDim,yDim,zDim) = BuildVtkImage.GetDimensions()

        shutil.rmtree('./test/testOutput/FullBlack/')
        os.mkdir('./test/testOutput/FullBlack/')

        blackSlicer.exportImage('./test/testOutput/FullBlack/','testImage')
        count = 0
        for file in os.listdir('./test/testOutput/FullBlack/'):
            if fnmatch.fnmatch(file,'testImage_*.bmp'):
                count = count + 1
        
        self.assertNotEqual(count, 0)
        self.assertEqual(count,zDim)

    def tearDown(self):
        os.remove("test.ini")