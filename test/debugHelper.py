import vtk

def visualizer(polydata):
    
    Renderer = vtk.vtkRenderer()
    RendererWindow = vtk.vtkRenderWindow()
    RendererWindow.AddRenderer(Renderer)

    polymapper = vtk.vtkPolyDataMapper()
    polymapper.SetInputData(polydata)

    actor = vtk.vtkActor()
    actor.SetMapper(polymapper)

    Bound = actor.GetBounds()

    axes = vtk.vtkAxesActor()
    axes.SetTotalLength(Bound[1],Bound[3],Bound[5])

    Renderer.AddActor(actor)
    Renderer.AddActor(axes)
    Renderer.ResetCamera()

    Interactor = vtk.vtkRenderWindowInteractor()
    Interactor.SetRenderWindow(RendererWindow)
    Interactor.Initialize()
    RendererWindow.Render()
    Interactor.Start()

def visualizerActor(listactor):
    Renderer = vtk.vtkRenderer()
    RendererWindow = vtk.vtkRenderWindow()
    RendererWindow.AddRenderer(Renderer)

    for actor in listactor:
        Renderer.AddActor(actor)

    axes = vtk.vtkAxesActor()
    axes.SetTotalLength(30,30,30)
    Renderer.AddActor(axes)    
    Renderer.ResetCamera()

    Interactor = vtk.vtkRenderWindowInteractor()
    Interactor.SetRenderWindow(RendererWindow)
    Interactor.Initialize()
    RendererWindow.Render()
    Interactor.Start()