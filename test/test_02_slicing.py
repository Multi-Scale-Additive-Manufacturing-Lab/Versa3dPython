import unittest
from src.lib.slicing import slicerFactory, FullBlackImageSlicer,CheckerBoardImageSlicer
from src.lib.versa3dConfig import FillEnum
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