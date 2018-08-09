import unittest
import test.debugHelper as db
import vtk
import src.lib.polyskel as sk       

class skeletonizeTest(unittest.TestCase):

    def setUp(self):
        reader = vtk.vtkSTLReader()
        reader.SetFileName('./test/testFile/3DBenchySmall.stl')
        reader.Update()

        stl_poly_data = reader.GetOutput()

        bounds = stl_poly_data.GetBounds()

        cut_plane = vtk.vtkPlane()
        cut_plane.SetOrigin(0,0,0)
        cut_plane.SetNormal(0,0,1)
        cut_plane.SetOrigin(0,0,(bounds[5]-bounds[4])/2)

        cutter = vtk.vtkCutter()
        cutter.SetCutFunction(cut_plane)
        cutter.SetInputConnection(reader.GetOutputPort())

        self.stripper = vtk.vtkStripper()
        self.stripper.SetInputConnection(cutter.GetOutputPort())
        self.stripper.Update()

        transform = vtk.vtkTransform()
        transform.Translate([10,10,(bounds[5]-bounds[4])/2])

        self.LocalToWorldCoordConverter = vtk.vtkTransformPolyDataFilter()
        self.LocalToWorldCoordConverter.SetTransform(transform)
        self.LocalToWorldCoordConverter.SetInputConnection(self.stripper.GetOutputPort())
        self.LocalToWorldCoordConverter.Update()

    def test_generate_skeleton(self):
        skeleton = sk.vtk_skeletonize()
        skeleton.DebugOn()

        skeleton.SetInputConnection(self.LocalToWorldCoordConverter.GetOutputPort())
        skeleton.set_shell_thickness(0.2)
        skeleton.Update()

        db.visualizer(skeleton.GetOutputDataObject(0))

    
    def tearDown(self):
        pass
