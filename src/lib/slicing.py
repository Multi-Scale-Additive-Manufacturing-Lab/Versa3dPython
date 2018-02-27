import vtk

def slicerFactory(type):
    
    if('black' == type):
        return FullBlackImageSlicer()
    elif('checker_board'==type):
        return CheckerBoardImageSlicer()
    else:
        return None
    

class FullBlackImageSlicer():

    def __init__(self, thickness = 0.1):
        self._thickness = 0.1
        self._listOfShape = []
    
    def addShape(self, shape):
        self._listOfShape.append(shape)

    def slice(self):
        for geometry in self._listOfShape:
            pass
    
    def exportImage(self):
        pass

class CheckerBoardImageSlicer():

    def __init__(self):
        pass
