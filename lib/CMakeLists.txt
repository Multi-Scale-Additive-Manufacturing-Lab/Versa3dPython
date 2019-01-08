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

## google test ##

# Download and unpack googletest at configure time
configure_file(CMakeLists.txt.in googletest-download/CMakeLists.txt)
execute_process(COMMAND "${CMAKE_COMMAND}" -G "${CMAKE_GENERATOR}" .
    WORKING_DIRECTORY "${CMAKE_BINARY_DIR}/googletest-download" )
execute_process(COMMAND "${CMAKE_COMMAND}" --build .
    WORKING_DIRECTORY "${CMAKE_BINARY_DIR}/googletest-download" )

# Prevent GoogleTest from overriding our compiler/linker options
# when building with Visual Studio
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)

# Add googletest directly to our build. This adds
# the following targets: gtest, gtest_main, gmock
# and gmock_main
add_subdirectory("${CMAKE_BINARY_DIR}/googletest-src"
                 "${CMAKE_BINARY_DIR}/googletest-build")
