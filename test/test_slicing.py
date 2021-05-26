import unittest

from vtkmodules.vtkIOGeometry import vtkSTLReader
from vtkmodules.vtkCommonDataModel import vtkPolyData, vtkImageData

from versalib import VoxelizerFilter, pass_port

class SlicingTest(unittest.TestCase):

    def check_poly(self, poly):
        self.assertIsInstance(poly, vtkImageData)

    def setUp(self):
        self.reader = vtkSTLReader()
        self.reader.SetFileName('./test/test_file/3DBenchySmall.stl')
        self.reader.Update()

    def test_slice_boat(self):
        port = self.reader.GetOutputPort()
        img = pass_port(port)
        self.check_poly(img)


if __name__ == '__main__':
    unittest.main()
