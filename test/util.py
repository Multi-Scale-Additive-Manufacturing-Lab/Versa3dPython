import vtk

def render_polydata(poly):
    poly_mapper = vtk.vtkPolyDataMapper()
    poly_mapper.SetInputData(poly)

    actor = vtk.vtkActor()
    actor.SetMapper(poly_mapper)

    ren = vtk.vtkRenderer()
    ren_win = vtk.vtkRenderWindow()
    ren_win.AddRenderer(ren)

    ren_win_int = vtk.vtkRenderWindowInteractor()
    ren_win_int.SetRenderWindow(ren_win)

    ren.AddActor(actor)
    ren_win.Render()
    ren_win_int.Start()

def render_image(img):
    im_mapper = vtk.vtkDataSetMapper()
    im_mapper.SetInputData(img)

    actor = vtk.vtkActor()
    actor.SetMapper(im_mapper)

    ren = vtk.vtkRenderer()
    ren_win = vtk.vtkRenderWindow()
    ren_win.AddRenderer(ren)

    ren_win_int = vtk.vtkRenderWindowInteractor()
    ren_win_int.SetRenderWindow(ren_win)

    ren.AddActor(actor)
    ren_win.Render()
    ren_win_int.Start()