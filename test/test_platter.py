import unittest
import vtk
from test.util import render_polydata
from versa3d.print_platter import PrintPlatterSource, PrintObject


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

            obj = PrintObject('sphere_{}'.format(i), source)

            self.list_sphere.append(obj)

    def test_add_sphere(self):
        platter = PrintPlatterSource()

        for i, obj in enumerate(self.list_sphere):
            platter.add_part('sphere_{}'.format(i), obj)

        platter.Update()
        poly_data = platter.GetOutputDataObject(0)

        split = vtk.vtkConnectivityFilter()
        split.SetInputData(poly_data)
        split.SetExtractionModeToAllRegions()
        split.Update()
        n_output = split.GetNumberOfExtractedRegions()
        self.assertEqual(n_output, self.n_sphere)

    def test_remove_sphere(self):
        platter = PrintPlatterSource()

        for i, obj in enumerate(self.list_sphere):
            platter.add_part(i, obj)

        platter.Update()
        platter.remove_part(0)
        platter.Update()

        poly_data = platter.GetOutputDataObject(0)

        split = vtk.vtkConnectivityFilter()
        split.SetInputData(poly_data)
        split.SetExtractionModeToAllRegions()
        split.Update()
        n_output = split.GetNumberOfExtractedRegions()

        self.assertEqual(n_output, self.n_sphere - 1)


if __name__ == '__main__':
    unittest.main()
