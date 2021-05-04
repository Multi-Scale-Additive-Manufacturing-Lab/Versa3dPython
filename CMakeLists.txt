cmake_minimum_required(VERSION 3.12...3.16 FATAL_ERROR)

project(VersaLib)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
OPTION(BUILD_TEST "compile test" True) 

find_package(pybind11 REQUIRED)
find_package(VTK REQUIRED)
find_package(Catch2 REQUIRED)

include(${CMAKE_SOURCE_DIR}/versalib/CMakeLists.txt)

if(${BUILD_TEST})
    include(${CMAKE_SOURCE_DIR}/test/CMakeLists.txt)
endif()