import unittest
import vtk
import re
import os
import fnmatch
import shutil
from src.lib.slicing import slicerFactory, FullBlackImageSlicer,CheckerBoardImageSlicer , VoxelSlicer
from src.lib.versa3dConfig import FillEnum , config

class TestSlicer(unittest.TestCase):

    def setUp(self):
        pass
    
    def test_slicerFactory(self):
        AllBlackSlicer = slicerFactory('black')
        self.assertEqual(FullBlackImageSlicer, type(AllBlackSlicer))

        CheckBoardSlicer = slicerFactory('checker_board')
        self.assertEqual(CheckerBoardImageSlicer, type(CheckBoardSlicer))

        NullCase = slicerFactory(None)
        self.assertEqual(None,NullCase)

    def test_voxel(self):
        ren1 = vtk.vtkRenderer()
        renWin = vtk.vtkRenderWindow()
        renWin.AddRenderer(ren1)
        iren = vtk.vtkRenderWindowInteractor()
        iren.SetRenderWindow(renWin)

        sphereModel = vtk.vtkSphereSource()
        sphereModel.SetThetaResolution(10)
        sphereModel.SetPhiResolution(10)
        sphereModel.Update()

        sphereMapper = vtk.vtkPolyDataMapper()
        sphereMapper.SetInputData(sphereModel.GetOutput())
        sphereMapper.Update()

        sphereActor = vtk.vtkActor()
        sphereActor.SetMapper(sphereMapper)

        voxelModel = vtk.vtkVoxelModeller()
        voxelModel.SetInputData(sphereActor.GetMapper().GetInput())
        voxelModel.SetSampleDimensions(50, 50, 50)
        voxelModel.SetModelBounds(-1.5, 1.5, -1.5, 1.5, -1.5, 1.5)
        voxelModel.SetScalarTypeToBit()
        voxelModel.SetForegroundValue(1)
        voxelModel.SetBackgroundValue(0)
        voxelModel.Update()

        voxelSurface = vtk.vtkContourFilter()
        voxelSurface.SetInputData(voxelModel.GetOutput())
        voxelSurface.SetValue(0, .999)

        voxelMapper = vtk.vtkPolyDataMapper()
        voxelMapper.SetInputConnection(voxelSurface.GetOutputPort())

        voxelActor = vtk.vtkActor()
        voxelActor.SetMapper(voxelMapper)

        ren1.AddActor(voxelActor)
        ren1.SetBackground(.1, .2, .4)
        ren1.ResetCamera()
        iren.Initialize()
        iren.Start()

    def test_blackSlicing(self):
        
        testSphere = vtk.vtkPSphereSource()
        testSphere.SetPhiResolution(50)
        testSphere.SetThetaResolution(50)
        testSphere.SetRadius(20)
        testSphere.Update()

        testSphere2 = vtk.vtkPSphereSource()
        testSphere2.SetPhiResolution(50)
        testSphere2.SetThetaResolution(50)
        testSphere2.SetRadius(10)
        testSphere2.Update()

        sphereMapper = vtk.vtkPolyDataMapper()
        sphereMapper.SetInputData(testSphere.GetOutput())
        sphereMapper.Update()

        sphereMapper2 = vtk.vtkPolyDataMapper()
        sphereMapper2.SetInputData(testSphere2.GetOutput())
        sphereMapper2.Update()

        sphereActor = vtk.vtkActor()
        sphereActor.SetPosition(40,40,20)
        sphereActor.SetMapper(sphereMapper)

        sphereActor2 = vtk.vtkActor()
        sphereActor2.SetPosition(80,80,30)
        sphereActor2.SetMapper(sphereMapper2)
        
        test_config = config("test.ini")
        
        blackSlicer = FullBlackImageSlicer(test_config)
        blackSlicer.addActor(sphereActor)
        blackSlicer.addActor(sphereActor2)
        BuildVtkImage = blackSlicer.slice()

        os.remove("test.ini")

        vtkImageStat = vtk.vtkImageAccumulate()
        vtkImageStat.DebugOn()
        vtkImageStat.SetComponentSpacing(1,0,0)
        vtkImageStat.SetComponentExtent(0,1,0,0,0,0)
        vtkImageStat.SetComponentOrigin(0,0,0)
        vtkImageStat.SetInputData(BuildVtkImage)
        vtkImageStat.Update()
        

        totalVoxel = vtkImageStat.GetVoxelCount()
        meanArray = vtkImageStat.GetMean()
        self.assertEqual(64160000,totalVoxel)
        self.assertLessEqual(0.95,meanArray[0]/255)

        #uncomment if you want to visual check
        '''
        Renderer = vtk.vtkRenderer()
        RendererWindow = vtk.vtkRenderWindow()
        RendererWindow.AddRenderer(Renderer)

        (xMin,xMax,yMin,yMax,zMin,zMax) = BuildVtkImage.GetExtent()

        imageMapper = vtk.vtkImageSliceMapper()
        imageMapper.SetInputData(BuildVtkImage)
        imageMapper.BackgroundOn()
        imageMapper.SetOrientationToZ()
        imageMapper.SetSliceNumber(333)

        imageActor = vtk.vtkImageSlice()
        imageActor.SetMapper(imageMapper)

        Renderer.AddActor(imageActor)
        Renderer.ResetCamera()

        Interactor = vtk.vtkRenderWindowInteractor()
        Interactor.SetInteractorStyle(vtk.vtkInteractorStyleImage())
        Interactor.SetRenderWindow(RendererWindow)
        Interactor.Initialize()
        RendererWindow.Render()
        Interactor.Start()
        '''
        
    def test_BMPExport(self):
        testSphere = vtk.vtkPSphereSource()
        testSphere.SetPhiResolution(50)
        testSphere.SetThetaResolution(50)
        testSphere.SetRadius(20)
        testSphere.Update()

        testSphere2 = vtk.vtkPSphereSource()
        testSphere2.SetPhiResolution(50)
        testSphere2.SetThetaResolution(50)
        testSphere2.SetRadius(10)
        testSphere2.Update()

        sphereMapper = vtk.vtkPolyDataMapper()
        sphereMapper.SetInputData(testSphere.GetOutput())
        sphereMapper.Update()

        sphereMapper2 = vtk.vtkPolyDataMapper()
        sphereMapper2.SetInputData(testSphere2.GetOutput())
        sphereMapper2.Update()

        sphereActor = vtk.vtkActor()
        sphereActor.SetPosition(40,40,20)
        sphereActor.SetMapper(sphereMapper)

        sphereActor2 = vtk.vtkActor()
        sphereActor2.SetPosition(80,80,30)
        sphereActor2.SetMapper(sphereMapper2)
        
        test_config = config("test.ini")
        
        blackSlicer = FullBlackImageSlicer(test_config)
        blackSlicer.addActor(sphereActor)
        blackSlicer.addActor(sphereActor2)
        BuildVtkImage = blackSlicer.slice()

        os.remove("test.ini")

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