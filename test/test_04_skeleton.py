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
        cut_plane.SetOrigin(0,0,2.5)

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
        skeleton = sk.VtkSkeletonize()
        skeleton.DebugOn()
        #db.visualizer(self.LocalToWorldCoordConverter.GetOutput())
        
        skeleton.SetInputConnection(self.LocalToWorldCoordConverter.GetOutputPort())
        skeleton.set_shell_thickness(10)
        skeleton.Update()

        merge = vtk.vtkAppendPolyData()
        merge.AddInputData(skeleton.GetOutputDataObject(0))
        merge.AddInputData(self.LocalToWorldCoordConverter.GetOutput())
        merge.Update()

        db.visualizer(merge.GetOutput())
        
    
    def tearDown(self):
        pass
