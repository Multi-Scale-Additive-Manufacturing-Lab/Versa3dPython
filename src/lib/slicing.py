import vtk

def slicerFactory(type):
    
    if('black' == type):
        return FullBlackImageSlicer()
    elif('checker_board'==type):
        return CheckerBoardImageSlicer()
    else:
        return None
    

class FullBlackImageSlicer():

    def __init__(self):
        pass
    
    def addShape(self, shape):
        pass

    def slice(self):
        pass

    def preview(self):
        pass
    
    def exportImage(self):
        pass

class CheckerBoardImageSlicer():

    def __init__(self):
        pass
