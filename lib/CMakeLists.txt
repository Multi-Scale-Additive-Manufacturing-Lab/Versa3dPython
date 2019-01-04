cmake_minimum_required(VERSION 3.5)

find_package(VTK REQUIRED)
include(${VTK_USE_FILE})

SET(VTK_COMPONENT
    vtkCommonCore
    vtkCommonDataModel
    vtkFiltersCore
    vtkFiltersModeling
    vtkInteractionStyle
    vtkIOImage
    vtkImagingCore
    vtkImagingGeneral
    vtkImagingStatistics
    vtkImagingStencil
    vtkWrappingPythonCore
)

set(LIB_HEADERS 
    ${CMAKE_CURRENT_SOURCE_DIR}/include/converter.h
    ${CMAKE_CURRENT_SOURCE_DIR}/include/bmpwriter.h
    ${CMAKE_CURRENT_SOURCE_DIR}/include/PybindVTKTypeCaster.h
)

set(LIB_SRC
    ${CMAKE_CURRENT_SOURCE_DIR}/src/bmpwriter.cc
)

pybind11_add_module(Versa3dLib ${LIB_SRC} ${LIB_HEADERS})
#message(${VTK_LIBRARIES})

#in conda-forge vtk pkg, HDF5 dependencies path are hard coded
#target_link_libraries(Versa3lib PRIVATE ${VTK_LIBRARIES}) Fails
target_link_libraries(Versa3dLib PRIVATE ${VTK_COMPONENT})
target_include_directories(Versa3dLib PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include) 
