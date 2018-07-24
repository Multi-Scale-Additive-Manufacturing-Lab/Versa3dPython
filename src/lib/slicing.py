import vtk
import numpy as np
from src.lib.versa3dConfig import config
import math
import queue as q

from test.debugHelper import visualizer

def slicerFactory(config):

    if(config != None):
        type = config.getPrintSetting('fill')

        if('fblack' == type):
            return FullBlackImageSlicer(config)
        elif('checker_board'==type):
            return CheckerBoardImageSlicer(config)
        else:
            return None

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

def slicePoly(limit,increment,polydata):
    """slice polydata in z direction into contour
    
    Arguments:
        limit {list} -- min and max
        increment {float} -- thickness
        polydata {vtkpolydata} -- surface to slice
    
    Returns:
        list -- list of vtkpolydata contour
    """

    listOfContour = []

    for height in np.arange(limit[0],limit[1]+increment,increment):
        cutPlane = vtk.vtkPlane()
        cutPlane.SetOrigin(0,0,0)
        cutPlane.SetNormal(0,0,1)
        cutPlane.SetOrigin(0,0,height)

        cutter = vtk.vtkCutter()
        cutter.SetCutFunction(cutPlane)
        cutter.SetInputData(polydata)

        stripper = vtk.vtkStripper()
        stripper.SetInputConnection(cutter.GetOutputPort())
        
        stripper.Update()
        contour = stripper.GetOutput()
        listOfContour.append(contour)
    
    return listOfContour

class slice():
    def __init__(self, height,thickess):
        self._height = height
        self._thickness = thickess

        self._image = None

    def getThickness(self):
        return self._thickness
    
    def getHeight(self):
        return self._height
    
    def getImage(self):
        return self._image
    
    def setImage(self,image):
        self._image = image
 
class VoxelSlicer():
    def __init__(self, config):
        self._listOfActors = []
        
        self._buildBedSizeXY = config.getMachineSetting('printbedsize')

        self._buildHeight = config.getMachineSetting('buildheight')
        self._thickness = config.getPrintSetting('layer_thickness')
        dpi = config.getPrintHeadSetting('dpi')
        self._sliceStack = []

        self._buildBedVolPixel = [0]*2
        XYVoxelSize = [0]*2

        for i in range(0,2):
            self._buildBedVolPixel[i] = int(math.ceil(self._buildBedSizeXY[i]*dpi[i]/(0.0254*1000)))
            XYVoxelSize[i] = self._buildBedSizeXY[i]/self._buildBedVolPixel[i]

        self._spacing = XYVoxelSize+[self._thickness]

        self._extruder = vtk.vtkLinearExtrusionFilter()
        self._extruder.SetScaleFactor(1.)
        self._extruder.SetExtrusionTypeToNormalExtrusion()
        self._extruder.SetVector(0, 0, 1)

        self._poly2Sten = vtk.vtkPolyDataToImageStencil()
        self._poly2Sten.SetTolerance(0) #important for when SetVector is 0,0,1
        self._poly2Sten.SetOutputSpacing(self._spacing)
        self._poly2Sten.SetInputConnection(self._extruder.GetOutputPort())
        
        self._imgstenc = vtk.vtkImageStencil()
        self._imgstenc.SetStencilConnection(self._poly2Sten.GetOutputPort())
        self._imgstenc.ReverseStencilOn()
        self._imgstenc.SetBackgroundValue(0)

    def _mergePoly(self):
        """internal function that merge all the actors into a single polydata. 
        polydata is in world coord
        
        Returns:
            vtkPolydata -- surface
        """

        merge = vtk.vtkAppendPolyData()
        clean = vtk.vtkCleanPolyData()

        for actor in self._listOfActors:

            transform = vtk.vtkTransform()
            transform.SetMatrix(actor.GetMatrix())

            PolyData = vtk.vtkPolyData()
            PolyData.DeepCopy(actor.GetMapper().GetInput())

            LocalToWorldCoordConverter = vtk.vtkTransformPolyDataFilter()
            LocalToWorldCoordConverter.SetTransform(transform)
            LocalToWorldCoordConverter.SetInputData(PolyData)
            LocalToWorldCoordConverter.Update()

            Extent = actor.GetBounds()

            merge.AddInputData(LocalToWorldCoordConverter.GetOutput())

        merge.Update()
        clean.SetInputConnection(merge.GetOutputPort())
        clean.Update()

        return clean.GetOutput()
        
    def addActor(self, actor):
        self._listOfActors.append(actor)
    
    def getBuildVolume(self):
        return self._sliceStack
    def getXYDim(self):
        return self._buildBedVolPixel
    def getSlice(self,index):
        return self._sliceStack[i]

class FullBlackImageSlicer(VoxelSlicer):

    def __init__(self, config):
        super().__init__(config)
        
    def slice(self):
        
        mergedPoly = self._mergePoly()

        mergedPoly.ComputeBounds()
        bound = mergedPoly.GetBounds()
        
        imgDim = [1]*3
        for i in range(0,2):
            imgDim[i] = int(math.ceil((bound[2*i+1]-bound[2*i])/self._spacing[i]))+1

        whiteImage = vtk.vtkImageData()
        whiteImage.SetSpacing(self._spacing)
        whiteImage.SetDimensions(imgDim)
        whiteImage.AllocateScalars(vtk.VTK_UNSIGNED_CHAR,1)
        whiteImage.GetPointData().GetScalars().Fill(255) 
        self._imgstenc.SetInputData(whiteImage)

        listOfContour = slicePoly(bound[4:6],self._thickness,mergedPoly)

        for contour in listOfContour:

            origin = [0]*3
            ContourBounds = contour.GetBounds()
            origin[0] = bound[0]
            origin[1] = bound[2]
            origin[2] = ContourBounds[4]

            IndividualSlice = slice(origin[2],self._thickness)
            
            #white image origin and stencil origin must line up
            whiteImage.SetOrigin(origin)

            if(contour.GetNumberOfLines() > 0):
                self._extruder.SetInputData(contour)
                self._extruder.Update()
                
                self._poly2Sten.SetOutputOrigin(origin)
                self._poly2Sten.Update()

                self._imgstenc.Update()
                image = vtk.vtkImageData()
                image.ShallowCopy(self._imgstenc.GetOutput())
                IndividualSlice.setImage(image)
                self._sliceStack.append(IndividualSlice)

        return self._sliceStack

class CheckerBoardImageSlicer(VoxelSlicer):

    def __init__(self, config):
        super().__init__(config)
    
    def slice(self):

        mergedPoly = self._mergePoly()
        mergedPoly.ComputeBounds()
        bound = mergedPoly.GetBounds()

        listOfContour = slicePoly(bound[4:6],self._thickness,mergedPoly)