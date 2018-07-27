import unittest
import vtk
import test.debugHelper as db

class skeletonizeTest(unittest.TestCase):

    def setUp(self):
        reader = vtk.vtkSTLReader()
        reader.SetFileName('./test/testFile/3DBenchySmall.stl')
        reader.Update()

        stl_poly_data = reader.GetOutput()

        bounds = stl_poly_data.GetBounds()

        cutPlane = vtk.vtkPlane()
        cutPlane.SetOrigin(0,0,0)
        cutPlane.SetNormal(0,0,1)
        cutPlane.SetOrigin(0,0,(bounds[5]-bounds[4])/2)

        cutter = vtk.vtkCutter()
        cutter.SetCutFunction(cutPlane)
        cutter.SetInputData(stl_poly_data)

        stripper = vtk.vtkStripper()
        stripper.SetInputConnection(cutter.GetOutputPort())

        stripper.Update()
        self.contour = stripper.GetOutput()
    
    def test_generateSkeleton(self):
        #db.visualizer(self.contour)
        pass
    
    def tearDown(self):
        pass