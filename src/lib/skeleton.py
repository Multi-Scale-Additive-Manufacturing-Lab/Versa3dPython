import vtk
import numpy as np
import queue as q

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