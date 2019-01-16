import unittest
import os
from src.lib.versa3dConfig import config
from src.lib.gcode import gcodeWriterVlaseaBM
import src.lib.slicing as sl
import shutil
import vtk


class gcodeTest(unittest.TestCase):

    def setUp(self):
        self.testConfigFolder = './configtest'

        if(not os.path.isdir('./test/testOutput')):
            os.mkdir('./test/testOutput')

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

        if(zRange[0] < 0):
            newPosition[2] = oldPosition[2]-zRange[0]
        else:
            newPosition[2] = oldPosition[2]

        self.stlActor.SetPosition(newPosition)
        self.stlActor.RotateZ(45)

    def test_generategcode(self):
        output_folder_black = os.path.join('.', 'test', 'testOutput', 'Gcode')

        if(not os.path.isdir(output_folder_black)):
            os.mkdir(output_folder_black)
        else:
            shutil.rmtree(output_folder_black)
            os.mkdir(output_folder_black)

        blackSlicer = sl.FullBlackImageSlicer(self.test_config)
        blackSlicer.addActor(self.stlActor)
        BuildVtkImage = blackSlicer.slice()

        gcodewriter = gcodeWriterVlaseaBM(
            self.test_config, output_folder_black)
        gcodewriter.SetInput(blackSlicer)
        gcodewriter.generateGCode()

    def test_generate_gcode_checkerboard(self):

        output_folder_check = os.path.join(
            '.', 'test', 'testOutput', 'GcodeCheck')

        if(not os.path.isdir(output_folder_check)):
            os.mkdir(output_folder_check)
        else:
            shutil.rmtree(output_folder_check)
            os.mkdir(output_folder_check)

        checker_board_slicer = sl.CheckerBoardImageSlicer(self.test_config)
        checker_board_slicer.addActor(self.stlActor)
        checker_board_slicer.slice()

        gcodewriter = gcodeWriterVlaseaBM(
            self.test_config, output_folder_check)
        gcodewriter.SetInput(checker_board_slicer)
        gcodewriter.generateGCode()

    def test_generate_spread(self):

        output_folder_check = './test/testOutput/Spread'

        if(not os.path.isdir(output_folder_check)):
            os.mkdir(output_folder_check)
        else:
            shutil.rmtree(output_folder_check)
            os.mkdir(output_folder_check)

        gcodewriter = gcodeWriterVlaseaBM(
            self.test_config, output_folder_check)
        gcodewriter.test_spread()

    def tearDown(self):
        shutil.rmtree(self.testConfigFolder)
