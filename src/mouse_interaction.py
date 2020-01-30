import vtk

def actor_highlight(obj, ev):
    style = obj.GetInteractorStyle()
    style.SetCurrentStyleToTrackballActor()