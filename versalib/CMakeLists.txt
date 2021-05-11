
set(SRC_FILES 
    src/VoxDithering.cc
    src/VoxelizerFilter.cc
)

set(HEADER_FILES
    include/VoxDithering.h
    include/VoxelizerFilter.h
)

set(
    LIB_SRC_WRAP
    src/VersaLib_wrapper.cc
)

add_library(VersaLibCore ${SRC_FILES} ${HEADER_FILES})

target_link_libraries(VersaLibCore PRIVATE ${VTK_LIBRARIES})
target_include_directories(VersaLibCore PUBLIC include) 

pybind11_add_module(VersaLibPython ${LIB_SRC_WRAP})
target_link_libraries(VersaLibPython PUBLIC VersaLibCore)