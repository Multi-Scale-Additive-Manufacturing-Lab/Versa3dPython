import vtk
import os


def gcodeFactory(type):
    
    if('big_machine' == type):
        return big_machine()
    else:
        return None

class big_machine():

    def __init__(self):
        pass

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
        