cmake_minimum_required(VERSION 3.12...3.16 FATAL_ERROR)

project(VersaLib)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
include(CTest)

find_package(VTK REQUIRED)
find_package(Catch2 REQUIRED)

include(GNUInstallDirs)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_BINDIR}")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR}")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR}")

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

vtk_module_python_default_destination(python_destination)

# Build the module we just scanned.
vtk_module_build(MODULES ${modules})

# Wrap it with Python.
vtk_module_wrap_python(
  MODULES         ${modules}
  PYTHON_PACKAGE  "VersaLibPython"
  MODULE_DESTINATION "${python_destination}"
  # Static Python modules are almost never wanted.
  BUILD_STATIC    OFF
  INSTALL_HEADERS OFF)

# Create an `__init__.py` for the wrapped module.
file(WRITE "${CMAKE_BINARY_DIR}/${python_destination}/VersaLibPython/__init__.py" "")


#if(${BUILD_TESTING})
#add_subdirectory(${CMAKE_SOURCE_DIR}/test)
#endif()