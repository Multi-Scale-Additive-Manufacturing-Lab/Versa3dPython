cmake_minimum_required(VERSION 3.13)

find_package(VTK REQUIRED)
include(${VTK_USE_FILE})

pybind11_add_module(${CMAKE_PROJECT_NAME} src/test.cc)

target_link_libraries(${CMAKE_PROJECT_NAME} ${VTK_LIBRARIES})