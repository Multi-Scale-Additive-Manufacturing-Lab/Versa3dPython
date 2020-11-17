import unittest
import vtk
from versa3d.print_platter import PrintObject

class PlatterTest(unittest.TestCase):

    def setUp(self):
        self.n_sphere = 3
        self.list_sphere = []
        for i in range(self.n_sphere):
            source = vtk.vtkSphereSource()

            # random position and radius
            x = vtk.vtkMath.Random(0, 50)
            y = vtk.vtkMath.Random(0, 50)
            z = vtk.vtkMath.Random(0, 100)
            radius = vtk.vtkMath.Random(.5, 1.0)

            source.SetRadius(radius)
            source.SetCenter(x, y, z)
            source.SetPhiResolution(11)
            source.SetThetaResolution(21)

            obj = PrintObject(source)
            obj.saturation = 0.8
            obj.infill = 'black'
            obj.Update()

            self.list_sphere.append(obj)

    def test_add_sphere(self):
        platter = vtk.vtkAppendPolyData()
        for obj in self.list_sphere:
            platter.AddInputData(obj.GetOutputDataObject(0))

        platter.Update()
        poly_data = platter.GetOutput()

        split = vtk.vtkConnectivityFilter()
        split.SetInputData(poly_data)
        split.SetExtractionModeToAllRegions()
        split.Update()
        n_output = split.GetNumberOfExtractedRegions()
        self.assertEqual(n_output, self.n_sphere)

    def test_remove_sphere(self):
        platter = vtk.vtkAppendPolyData()
        for obj in self.list_sphere:
            platter.AddInputData(obj.GetOutputDataObject(0))
            
        poly_data = platter.GetOutput()

        platter.Update()
        platter.RemoveInputData(self.list_sphere[0].GetOutputDataObject(0))
        platter.Update()

        poly_data = platter.GetOutput()

        split = vtk.vtkConnectivityFilter()
        split.SetInputData(poly_data)
        split.SetExtractionModeToAllRegions()
        split.Update()
        n_output = split.GetNumberOfExtractedRegions()

        self.assertEqual(n_output, self.n_sphere - 1)


if __name__ == '__main__':
    unittest.main()
