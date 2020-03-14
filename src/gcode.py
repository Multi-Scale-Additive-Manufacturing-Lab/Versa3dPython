import vtk
from PIL import Image
import os


def gcodeFactory():
    pass

class LinuxCncWriter():

    def __init__(self, slicer):
        self._slicer = slicer

    def write_file(self, folder_path, slicer):
        pass
    
    def home_axis(self, axis):
        pass

    def move_axis(self, speed, pos, axis):
        pass

    def jog_axis(self, speed, pos, axis):
        pass

    def print_image(self, img_id):
        pass
        