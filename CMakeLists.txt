cmake_minimum_required(VERSION 3.5)
project(Versa3d)

set (CMAKE_CXX_STANDARD 14)
SET(PYBIND11_PYTHON_VERSION 3.6)

find_package(CGAL REQUIRED)
find_package(CGAL REQUIRED COMPONENTS Core)

## google test ##

# Download and unpack googletest at configure time
configure_file(google.txt.in googletest-download/CMakeLists.txt)
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

 ## vtk ## 
 configure_file(vtk.txt.in vtk-download/CMakeLists.txt)
 execute_process(COMMAND "${CMAKE_COMMAND}" -G "${CMAKE_GENERATOR}" .
    WORKING_DIRECTORY "${CMAKE_BINARY_DIR}/vtk-download" )
    
execute_process(COMMAND "${CMAKE_COMMAND}" --build .
    WORKING_DIRECTORY "${CMAKE_BINARY_DIR}/vtk-download" )         

########################
add_subdirectory(thirdparty/pybind11)
add_subdirectory(lib)

