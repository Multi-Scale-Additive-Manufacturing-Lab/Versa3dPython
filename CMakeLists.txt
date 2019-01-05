cmake_minimum_required(VERSION 3.5)
project(Versa3d)

set (CMAKE_CXX_STANDARD 11)
SET(PYBIND11_PYTHON_VERSION 3.6)

add_subdirectory(pybind11)
add_subdirectory(lib)
