import vtk
from PIL import Image
import os

from versa3d.settings import PrinterSettings, PrintheadSettings, PrintSettings


def GcodeWriterFactory():
    def __init__(self, slicer, print_setting, printer_name, printhead_name):
        self._slicer = slicer
        self._print_set = print_setting
        self._printer = printer_name
        self._printhead = printhead_name

    def create_writer(self, writer_type):
        if('LinuxCnc' == writer_type):
            return LinuxCncWriter(self._slicer, self._print_set, self._printer)
        else:
            return None


class LinuxCncWriter():

    def __init__(self, slicer, print_preset_name, printer_name):
        self._slicer = slicer

        print_settings = PrintSettings(print_preset_name)
        printer_attr = PrinterSettings(printer_name)

        self._printer_dim = printer_attr.bds

        self._printspeed = print_settings.ps
        self._H = print_settings.pho
        self._S = print_settings.pl
        self._W = print_settings.rwd
        self._feed_bed_vel = print_settings.fbv
        self._build_bed_velocity = print_settings.bbv

        self._print_bed_offset = printer_attr.coord_o

        self._roller_lin_vel = print_settings.rol_lin
        self._roller_rot_vel = print_settings.rol_rpm

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
