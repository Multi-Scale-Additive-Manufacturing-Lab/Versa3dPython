
set(SRC_FILES 
    src/VoxDithering.cc
    src/VoxelizerFilter.cc
    src/VoxShelling.cc
)

set(HEADER_FILES
    include/VoxDithering.h
    include/VoxelizerFilter.h
    include/VoxShelling.h
)

vtk_module_add_module(versa3d::versalib
  SOURCES ${SRC_FILES}
  HEADERS ${HEADER_FILES}
)

vtk_module_include(versa3d::versalib
    PUBLIC "include/"
)
