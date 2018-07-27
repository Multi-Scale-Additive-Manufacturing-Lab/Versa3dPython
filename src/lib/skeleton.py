import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
import numpy as np
import queue as q

class Skeletonize(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self, nInputPorts=1, inputType='vtkPolyData',
                                        nOutputPorts=1, outputType='vtkPolyData')
        
        self._thickness = 0.1
    
    def set_shell_thickness(self, thickness):
        self._thickness = thickness
        self.Modified()

    def RequestData(self, request, inInfo, outInfo):
        inp = vtk.vtkPolyData.GetData(inInfo[0])
        opt = vtk.vtkPolyData.GetData(outInfo)
        opt.DeepCopy(inp)
        
        line_iterator = opt.GetLines()
        line_iterator.InitTraversal()

        id_list = vtk.vtkIdList()
        listOfBisector = []
        while(line_iterator.GetNextCell(id_list)):
            length = id_list.GetNumberOfIds()

            for i in range(3):
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

        return 1

def find_bisector(vertex,prev_vertex,next_vertex):

    edge1 = prev_vertex - vertex
    edge2 = next_vertex - vertex
    
    ratio = np.linalg.norm(edge1)/np.linalg.norm(edge2)

    edge3 = (prev_vertex - next_vertex)

    bisector_point = np.linalg.norm(edge3)/(ratio+1)*edge3+next_vertex
    vector = (bisector_point-vertex)
    normalized_vector = vector/np.linalg.norm(vector)
    
    return normalized_vector+vertex

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
