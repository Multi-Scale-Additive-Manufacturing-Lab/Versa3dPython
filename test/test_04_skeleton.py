import unittest
import test.debugHelper as db
import vtk
import src.lib.polyskel as sk
import os
import shutil


def writer_poly(folderPath, polydata, count):
    writer = vtk.vtkPolyDataWriter()

    if(not os.path.isdir(folderPath)):
        os.mkdir(folderPath)
    else:
        shutil.rmtree(folderPath)
        os.mkdir(folderPath)

    imgFullPath = os.path.join(folderPath, 'contour_%d.vtp' % (count))
    writer.SetFileName(imgFullPath)
    writer.SetInputData(polydata)
    writer.SetFileTypeToASCII()
    writer.Write()


class skeletonizeTest(unittest.TestCase):

    def setUp(self):
        reader = vtk.vtkSTLReader()
        reader.SetFileName('./test/testFile/3DBenchySmall.stl')
        reader.Update()

        stl_poly_data = reader.GetOutput()

        bounds = stl_poly_data.GetBounds()

        transform = vtk.vtkTransform()
        transform.Translate([10, 10, -1*bounds[4]])
        #transform.Scale(1000000,1000000,1000000)

        CoordConverter = vtk.vtkTransformPolyDataFilter()
        CoordConverter.SetTransform(transform)
        CoordConverter.SetInputConnection(reader.GetOutputPort())
        CoordConverter.Update()

        self.height = CoordConverter.GetOutput().GetBounds()[5]

        self.cut_plane = vtk.vtkPlane()
        self.cut_plane.SetOrigin(0, 0, 0)
        self.cut_plane.SetNormal(0, 0, 1)
        self.cut_plane.SetOrigin(0, 0, 1)

        self.cutter = vtk.vtkCutter()
        self.cutter.SetCutFunction(self.cut_plane)
        self.cutter.SetInputConnection(
            CoordConverter.GetOutputPort())

        self.stripper = vtk.vtkStripper()
        self.stripper.SetInputConnection(self.cutter.GetOutputPort())
        self.stripper.JoinContiguousSegmentsOn()
        self.stripper.Update()

    def test_generate_skeleton(self):

        folderPath = './test/testOutput/skeleton'

        skeleton = sk.VtkSkeletonize()
        skeleton.DebugOn()

        skeleton.SetInputConnection(self.stripper.GetOutputPort())
        skeleton.set_shell_thickness(0.1)

        bounds = self.stripper.GetOutput().GetBounds()
        height = int(self.height)
        #for i in range(height):
        self.cut_plane.SetOrigin(0, 0, 3)
        self.cutter.Update()
        self.stripper.Update()
        #db.visualizer(self.stripper.GetOutput())
        skeleton.Update()

        merge = vtk.vtkAppendPolyData()
        merge.AddInputData(skeleton.GetOutputDataObject(0))
        merge.AddInputData(self.stripper.GetOutput())
        merge.Update()

        db.visualizer(merge.GetOutput())

        #writer_poly(folderPath, merge.GetOutput(), i)

    def tearDown(self):
        pass
