import unittest
import vtk
import re
import os
import fnmatch
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
        testSphere.SetRadius(10)
        testSphere.Update()

        sphereMapper = vtk.vtkPolyDataMapper()
        sphereMapper.SetInputData(testSphere.GetOutput())
        sphereMapper.Update()

        sphereActor = vtk.vtkActor()
        sphereActor.SetPosition(40,40,20)
        sphereActor.SetMapper(sphereMapper)
        
        test_config = config("test.ini")
        
        blackSlicer = FullBlackImageSlicer(test_config)
        blackSlicer.addActor(sphereActor)
        listOfSlice = blackSlicer.slice()

        self.assertEqual(200,len(listOfSlice))

        for EachSlice in listOfSlice:
            self.assertNotEqual(0, EachSlice.GetNumberOfPoints())
        
        os.remove("test.ini")

        #uncomment if you want to visual check
        '''
        Renderer = vtk.vtkRenderer()
        RendererWindow = vtk.vtkRenderWindow()
        RendererWindow.AddRenderer(Renderer)
        
        for EachSlice in listOfSlice:

            voxelSurface = vtk.vtkContourFilter()
            voxelSurface.SetInputData(EachSlice)
            voxelSurface.SetValue(0,0.999)

            voxelMapper = vtk.vtkPolyDataMapper()
            voxelMapper.SetInputConnection(voxelSurface.GetOutputPort())

            voxelActor = vtk.vtkActor()
            voxelActor.SetMapper(voxelMapper)
            Renderer.AddActor(voxelActor)
        
        Renderer.ResetCamera()

        Interactor = vtk.vtkRenderWindowInteractor()
        Interactor.SetInteractorStyle(vtk.vtkInteractorStyleSwitch())
        Interactor.SetRenderWindow(RendererWindow)

        Interactor.Initialize()
        RendererWindow.Render()
        Interactor.Start()
        '''

    def test_BMPExport(self):
        testSphere = vtk.vtkPSphereSource()
        testSphere.SetPhiResolution(50)
        testSphere.SetThetaResolution(50)
        testSphere.SetRadius(10)
        testSphere.Update()

        sphereMapper = vtk.vtkPolyDataMapper()
        sphereMapper.SetInputData(testSphere.GetOutput())
        sphereMapper.Update()

        sphereActor = vtk.vtkActor()
        sphereActor.SetPosition(40,40,20)
        sphereActor.SetMapper(sphereMapper)
        
        test_config = config("test.ini")
        
        blackSlicer = FullBlackImageSlicer(test_config)
        blackSlicer.addActor(sphereActor)
        listOfSlice = blackSlicer.slice()

        os.remove("test.ini")

        blackSlicer.exportImage('./test/testOutput/FullBlack/','testImage')
        count = 0
        for file in os.listdir('.'):
            if fnmatch.fnmatch(file,'./test/testOutput/FullBlack/testImage_*.bmp'):
                count = count + 1
        
        self.assertNotEqual(count, 0)
        self.assertEqual(count,200)