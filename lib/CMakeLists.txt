cmake_minimum_required(VERSION 3.5)

find_package(VTK REQUIRED)
include(${VTK_USE_FILE})

set(LIB_HEADERS 
    ${CMAKE_CURRENT_SOURCE_DIR}/include/converter.h
    ${CMAKE_CURRENT_SOURCE_DIR}/include/bmpwriter.h
)

set(LIB_SRC
    ${CMAKE_CURRENT_SOURCE_DIR}/src/bmpwriter.cc
)

pybind11_add_module(Versa3dLib ${LIB_SRC} ${LIB_HEADERS})

target_link_libraries(Versa3dLib PRIVATE vtkCommonCore)
target_include_directories(Versa3dLib PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include) 
