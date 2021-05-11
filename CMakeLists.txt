cmake_minimum_required(VERSION 3.12...3.16 FATAL_ERROR)

project(VersaLib)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
include(CTest)

find_package(pybind11 REQUIRED)
find_package(VTK REQUIRED)
find_package(Catch2 REQUIRED)

add_subdirectory(${CMAKE_SOURCE_DIR}/versalib)

if(${BUILD_TESTING})
add_subdirectory(${CMAKE_SOURCE_DIR}/test)
endif()