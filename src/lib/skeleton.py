import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
import numpy as np
import queue as q
import test.debugHelper as db

class Skeletonize(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self, nInputPorts=1, inputType='vtkPolyData',
                                        nOutputPorts=1, outputType='vtkPolyData')
        
        self._thickness = 0.1
    
    def set_shell_thickness(self, thickness):
        self._thickness = thickness
        self.Modified()
    
    def is_clock_wise(self,polydata,id_list):
        length = id_list.GetNumberOfIds()
        sum = 0
        for i in range(length-1):
            vertex_id = id_list.GetId(i)
            next_vertex_id = id_list.GetId(i+1)

            vertex = polydata.GetPoint(vertex_id)
            next_vertex = polydata.GetPoint(next_vertex_id)
            sum += (next_vertex[0]-vertex[0])*(next_vertex[1]-vertex[1])

        if(sum >= 0):
            return True
        
        return False
    
    def is_collinear(self,prev_vertex,vertex,next_vertex):
        edge1 = prev_vertex - vertex
        edge2 = vertex - next_vertex

        cross_product = np.cross(edge1,edge2)
        if(np.linalg.norm(cross_product) == 0):
            return True
        else:
            return False
    
    def remove_collinear(self,polydata):
        out = vtk.vtkPolyData()

        contour = vtk.vtkCellArray()
        pts = vtk.vtkPoints()

        line_iterator = polydata.GetLines()
        line_iterator.InitTraversal()

        id_list = vtk.vtkIdList()

        while(line_iterator.GetNextCell(id_list)):
            length = id_list.GetNumberOfIds()
            polyLine = vtk.vtkPolyLine()

            deleted_ids = []

            for i in range(length-1):
                prev_vertex_id = id_list.GetId((i-1)%length)
                vertex_id = id_list.GetId(i)
                next_vertex_id =  id_list.GetId((i+1)%length)

                if(prev_vertex_id == vertex_id ):
                    prev_vertex_id = id_list.GetId((i-2)%length)
                elif(not prev_vertex_id in deleted_ids):
                    count = 2 
                    while(prev_vertex_id in deleted_ids):
                        prev_vertex_id = id_list.GetId((i-count)%length)
                        count += 1

                prev_vertex = np.array(polydata.GetPoint(prev_vertex_id))
                vertex = np.array(polydata.GetPoint(vertex_id))
                next_vertex = np.array(polydata.GetPoint(next_vertex_id))
                
                if(self.is_collinear(prev_vertex,vertex,next_vertex)):
                    new_prev_v_id = pts.InsertNextPoint(prev_vertex)
                    new_next_v_id = pts.InsertNextPoint(next_vertex)

                    polyLine.GetPointIds().InsertUniqueId(new_prev_v_id)
                    polyLine.GetPointIds().InsertUniqueId(new_next_v_id)

                    deleted_ids.append(vertex_id)
                else:
                    new_prev_v_id = pts.InsertNextPoint(prev_vertex)
                    new_v_id = pts.InsertNextPoint(vertex)
                    new_next_v_id = pts.InsertNextPoint(next_vertex)
                    
                    polyLine.GetPointIds().InsertUniqueId(new_prev_v_id)
                    polyLine.GetPointIds().InsertUniqueId(new_v_id)
                    polyLine.GetPointIds().InsertUniqueId(new_next_v_id)
            
            new_id_num = polyLine.GetPointIds().GetNumberOfIds()
            first_id = polyLine.GetPointIds().GetId(0)
            last_id = polyLine.GetPointIds().GetId(new_id_num-1)

            if(first_id != last_id):
                polyLine.GetPointIds().InsertId(new_id_num,first_id)

            contour.InsertNextCell(polyLine)
        
        out.SetPoints(pts)
        out.SetLines(contour)
        return out

    def RequestData(self, request, inInfo, outInfo):
        inp = vtk.vtkPolyData.GetData(inInfo[0])
        opt = vtk.vtkPolyData.GetData(outInfo)
        opt.DeepCopy(self.remove_collinear(inp))
        """
        line_iterator = opt.GetLines()
        line_iterator.InitTraversal()

        id_list = vtk.vtkIdList()
        listOfBisector = []
        while(line_iterator.GetNextCell(id_list)):
            length = id_list.GetNumberOfIds()

            clock_wise = self.is_clock_wise(opt,id_list)

            if(not clock_wise):
                index_list = reversed(range(length-1))
            else:
                index_list = range(length-1)

            for i in index_list:
                prev_vertex_id = id_list.GetId((i-1)%length)
                vertex_id = id_list.GetId(i)
                next_vertex_id =  id_list.GetId((i+1)%length)

                if(prev_vertex_id == vertex_id):
                    prev_vertex_id = id_list.GetId((i-2)%length)

                prev_vertex = inp.GetPoint(prev_vertex_id)
                vertex = inp.GetPoint(vertex_id)
                next_vertex = inp.GetPoint(next_vertex_id)

                bisector_point = find_bisector(np.array(vertex),np.array(prev_vertex),np.array(next_vertex))

                points = vtk.vtkPoints()
                bisector_point_id = points.InsertNextPoint(bisector_point)

                line = vtk.vtkLine()
                line.GetPointIds().InsertNextId(vertex_id)
                line.GetPointIds().InsertNextId(bisector_point_id)
                
                listOfBisector.append(line)

        for line in listOfBisector:
            line_iterator.InsertNextCell(line)
        """
        return 1

def find_bisector(vertex,prev_vertex,next_vertex):

    edge1 = prev_vertex - vertex
    edge2 = next_vertex - vertex
    
    norm_edge1 = np.linalg.norm(edge1)
    norm_edge2 = np.linalg.norm(edge2)

    normalized_edge1 = edge1/norm_edge1
    normalized_edge2 = edge2/norm_edge2

    cross_product = np.cross(normalized_edge2,normalized_edge1)

    if(cross_product[2] > 0 ):
        bisector = normalized_edge1+normalized_edge2
    else:
        bisector = (normalized_edge1+normalized_edge2)*-1

    return bisector/np.linalg.norm(bisector)

def findInterceptPoint(line1, line2):
    origin1 = line1[0]
    origin2 = line2[0]

    Y = np.array(origin2-origin1)

    slope1 = line1[1]
    slope2 = line2[1]

    Xinverse = np.diag((slope1-slope2)**(-1))

    return np.matmul(Xinverse,Y)

def findDistanceToLine(Point, line):
    AP = line[0]-Point
    u = line[1]
    return abs(np.linalg.norm(np.cross(AP,u))/np.linalg.norm(u))

def offsetContour(contour,thickness):
    """Shelling algorithm, only works with continuous contour
    
    Arguments:
        contour {vtkPolyData} -- vtkPolyData containing lines
        thickness {float} -- set thickness of shell
    """

    if(contour.GetNumberOfLines() != 0):
        LineIterator = contour.GetLines()
        LineIterator.InitTraversal()

        idList = vtk.vtkIdList()

        VertexState = [False]*contour.GetNumberOfPoints()
        
        SLAV = []
        LAV = []
        InterceptQueue = q.PriorityQueue()

        while(LineIterator.GetNextCell(idList)):
            numID = idList.GetNumberOfIds()
            LAV = [idList.GetId(i)for i in range(numID)]
            if(LAV[0] == LAV[-1]):
                LAV.pop()
            SLAV.append(LAV)
        
        for LAV in SLAV:
            length = len(LAV)
            listofbisector = []
            #compute all bisector
            for i in range(length):
                PrevVertexId = LAV[(i-1)%length]
                VertexId = LAV[i]
                NextVertexId = LAV[(i+1)%length]

                PrevVertex = np.array(contour.GetPoint(PrevVertexId))
                Vertex = np.array(contour.GetPoint(VertexId))
                NextVertex = np.array(contour.GetPoint(NextVertexId))

                edge1 = Vertex - PrevVertex
                edge2 = NextVertex - Vertex
                
                ratio = np.linalg.norm(edge1)/np.linalg.norm(edge2)

                edge3 = (PrevVertex - NextVertex)

                bisector = ratio/(1+ratio)*edge3+PrevVertex

                normalizedBisector = bisector/np.linalg.norm(bisector)

                listofbisector.append(normalizedBisector)
            
            #Compute intercept
            for i in range(length):
                PrevBisector = listofbisector[(i-1)%length]
                Bisector = listofbisector[i]
                NextBisector = listofbisector[(i+1)%length]

                PrevVertex = np.array(contour.GetPoint(LAV[(i-1)%length]))
                Vertex = np.array(contour.GetPoint(LAV[i]))
                NextVertex = np.array(contour.GetPoint(LAV[(i+1)%length]))

                if(np.dot(Bisector,prevBisector) != 1):
                    I1 = findInterceptPoint(( PrevVertex, PrevBisector),(Vertex, Bisector))
                    I2 = findInterceptPoint(( NextVertex, NextBisector),(Vertex, Bisector))
                    
                    edge = NextVertex - Vertex

                    distToEdge1 = findDistanceToLine(I1,(Vertex,edge))
                    distToEdge2 = findDistanceToLine(I2,(Vertex,edge))
                    if(distToEdge1 > distToEdge2):
                        InterceptQueue.put((distToEdge1,[I1,PrevVertexId,VertexId]))
                    else:
                        InterceptQueue.put((distToEdge2,[I2,VertexId,NextVertexId]))
        
            while(not InterceptQueue.empty()):
                distToEdge, cluster = InterceptQueue.get()
                I, VaId,VbId = cluster
                if(not VertexState[VaId] and not VertexState[VbId]):
                    pass
                PrevVertex = np.array(contour.GetPoint(VaId))
