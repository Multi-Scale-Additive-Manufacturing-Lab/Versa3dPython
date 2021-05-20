cmake_minimum_required(VERSION 3.12...3.16 FATAL_ERROR)

project(VersaLib)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
include(CTest)

find_package(VTK REQUIRED)
find_package(Catch2 REQUIRED)
find_package(pybind11 REQUIRED)

include(GNUInstallDirs)

set(_shared_default ON)
get_target_property(_vtk_libtype VTK::CommonCore TYPE)
if (_vtk_libtype STREQUAL "STATIC_LIBRARY")
  set(_shared_default OFF)
endif ()

option(BUILD_SHARED_LIBS "Build shared or static libraries" "${_shared_default}")

vtk_module_scan(
  MODULE_FILES      "${CMAKE_CURRENT_SOURCE_DIR}/versalib/vtk.module"
  REQUEST_MODULES   VersaLib::VersaFilters
  PROVIDES_MODULES  modules
  ENABLE_TESTS      OFF)

# Build the module we just scanned.
vtk_module_build(MODULES ${modules})
add_subdirectory(${CMAKE_SOURCE_DIR}/versalibpython)

#if(${BUILD_TESTING})
#add_subdirectory(${CMAKE_SOURCE_DIR}/test)
#endif()