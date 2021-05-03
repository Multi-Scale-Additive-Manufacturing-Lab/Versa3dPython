
set(SRC_FILES 
    ${CMAKE_SOURCE_DIR}/versalib/src/VoxDithering.cc
    ${CMAKE_SOURCE_DIR}/versalib/src/VoxelizerFilter.cc
)

set(HEADER_FILES
    ${CMAKE_SOURCE_DIR}/versalib/include/VoxDithering.h
    ${CMAKE_SOURCE_DIR}/versalib/include/VoxelizerFilter.h
)

set(
    LIB_SRC_WRAP
    ${CMAKE_SOURCE_DIR}/versalib/src/VersaLib_wrapper.cc
)

add_library(VersaLibCore STATIC ${SRC_FILES} ${HEADER_FILES})
target_link_libraries(VersaLibCore PUBLIC ${VTK_LIBRARIES})
target_include_directories(VersaLibCore PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/versalib/include) 

pybind11_add_module(VersaLibPython ${LIB_SRC_WRAP})
target_link_libraries(VersaLibPython PUBLIC VersaLibCore)