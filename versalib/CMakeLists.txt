
set(classes
    VoxDithering
    VoxelizerFilter
    VoxShelling
)

vtk_module_add_module(versa3d::versalib
CLASSES ${classes})
