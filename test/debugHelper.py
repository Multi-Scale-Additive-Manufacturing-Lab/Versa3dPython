import vtk

def visualizer(polydata):
    
    Renderer = vtk.vtkRenderer()
    RendererWindow = vtk.vtkRenderWindow()
    RendererWindow.AddRenderer(Renderer)

    polymapper = vtk.vtkPolyDataMapper()
    polymapper.SetInputData(polydata)

    actor = vtk.vtkActor()
    actor.SetMapper(polymapper)
    
    Renderer.AddActor(actor)
    Renderer.ResetCamera()

    Interactor = vtk.vtkRenderWindowInteractor()
    Interactor.SetRenderWindow(RendererWindow)
    Interactor.Initialize()
    RendererWindow.Render()
    Interactor.Start()