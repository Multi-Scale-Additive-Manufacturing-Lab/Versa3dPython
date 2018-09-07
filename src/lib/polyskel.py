# -*- coding: utf-8 -*-

import itertools as it
import numpy as np
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
import vtk
import pyclipper as pc


class VtkSkeletonize(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self, nInputPorts=1, inputType='vtkPolyData',
                                        nOutputPorts=1, outputType='vtkPolyData')

        self._thickness = 0.1

    def _convert_polydata(self, polydata):
        cell_array = polydata.GetLines()

        cell_array.InitTraversal()

        id_list = vtk.vtkIdList()
        list_path = []
        while(cell_array.GetNextCell(id_list)):
            path = []
            number_id = id_list.GetNumberOfIds()
            for i in range(number_id - 1):
                vertex_id = id_list.GetId(i)
                vertex = polydata.GetPoint(vertex_id)
                path.append(vertex[0:2])

            list_path.append(path)

        return list_path

    def RequestData(self, request, inInfo, outInfo):
        inp = vtk.vtkPolyData.GetData(inInfo[0])
        opt = vtk.vtkPolyData.GetData(outInfo)

        center = inp.GetCenter()

        transform = vtk.vtkTransform()
        transform.Scale(1000, 1000, 1)
        transform.Translate(0, 0, -center[2])

        scaling_transform = vtk.vtkTransformPolyDataFilter()
        scaling_transform.SetTransform(transform)
        scaling_transform.SetInputData(inp)
        scaling_transform.Update()

        list_path = self._convert_polydata(scaling_transform.GetOutput())

        hole_detector = HoleDetector(list_path)
        hole_relationship = hole_detector.execute()
        list_offset = []
        for contour_index, holes in hole_relationship.items():
            pco = pc.PyclipperOffset()
            contour = list_path[contour_index]
            orientation_c = pc.Orientation(contour)
            if(not orientation_c):
                contour = reversed(contour)
            pco.AddPath(contour, pc.JT_ROUND, pc.ET_CLOSEDPOLYGON)
            offset = pco.Execute(-1*self._thickness)
            list_offset.append(offset)

            for hole_index in holes:
                pco_h = pc.PyclipperOffset()
                hole = list_path[hole_index]
                orientation_h = pc.Orientation(hole)
                if(orientation_h):
                    hole = reversed(hole)
                
                pco_h.AddPath(hole, pc.JT_ROUND, pc.ET_CLOSEDPOLYGON)
                hole_offset = pco_h.Execute(self._thickness)
                list_offset.append(hole_offset)
                
        polydata = vtk.vtkPolyData()
        vtk_cell_array = vtk.vtkCellArray()
        vtk_points = vtk.vtkPoints()
        for offset in list_offset:
            vtk_polyline = vtk.vtkPolyLine()
            for i in range(len(offset[0])):
                v = offset[0][i]
                v_id = vtk_points.InsertNextPoint(v[0],v[1],0)
                vtk_polyline.GetPointIds().InsertNextId(v_id)

            first_v = vtk_polyline.GetPointIds().GetId(0)
            vtk_polyline.GetPointIds().InsertNextId(first_v)

            vtk_cell_array.InsertNextCell(vtk_polyline)

        polydata.SetPoints(vtk_points)
        polydata.SetLines(vtk_cell_array)

        revert = vtk.vtkTransformPolyDataFilter()
        revert.SetTransform(transform.GetInverse())
        revert.SetInputData(polydata)
        revert.Update()

        opt.ShallowCopy(revert.GetOutput())        

        return 1

    def set_shell_thickness(self, thickness):
        self._thickness = thickness
        self.Modified()


class TreeNode():

    def __init__(self, index):
        self.children = []
        self.parent = None
        self.data = index

    def insert_child(self, node):
        self.children.append(node)
        node.parent = self

    def remove_child(self, node):
        self.children.remove(node)
        node.parent = None


class HoleDetector():
    def __init__(self, list_polygon):
        self._list_polygon = list_polygon

    def execute(self):
        list_contour_tree = []

        for i in range(len(self._list_polygon)):
            node = TreeNode(i)
            is_outside = True

            for contour in list_contour_tree:
                is_i_in_c = self.check(node.data, contour.data)
                if(is_i_in_c):
                    self.insert(contour, node)
                    is_outside = False
                    break
                else:
                    is_c_in_i = self.check(contour.data, node.data)
                    if(is_c_in_i):
                        node.insert_child(contour)
                        list_contour_tree.remove(contour)
                        is_outside = False
            if(is_outside):
                list_contour_tree.append(node)

        hole_dict = {}
        for node in list_contour_tree:
            self.convert_tree(node, False, hole_dict)

        return hole_dict

    def insert(self, parent, node):
        children = parent.children
        is_same_lvl = True
        for child in children:
            is_node_in_child = self.check(node.data, child.data)
            if(is_node_in_child):
                self.insert(child, node)
                is_same_lvl = False
                break
            else:
                is_child_in_node = self.check(child.data, node.data)
                if(is_child_in_node):
                    parent.remove_child(child)
                    node.insert_child(child)
                    parent.insert_child(node)
                    is_same_lvl = False

        if(is_same_lvl):
            parent.insert_child(node)

    def convert_tree(self, node, is_hole, contour_dict):

        current_index = node.data

        if(not is_hole):
            contour_dict[current_index] = []

        for child in node.children:
            self.convert_tree(child, not is_hole, contour_dict)

        if(is_hole):
            parent_index = node.parent.data
            contour_dict[parent_index].append(current_index)

    def check(self, poly_1_index, poly_2_index):
        poly_1 = self._list_polygon[poly_1_index]
        poly_2 = self._list_polygon[poly_2_index]

        for vert in poly_1:
            state = pc.PointInPolygon(vert, poly_2)
            if(state == 0):
                return False
        return True
