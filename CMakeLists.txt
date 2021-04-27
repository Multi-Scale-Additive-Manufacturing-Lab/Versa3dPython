cmake_minimum_required(VERSION 3.12...3.16 FATAL_ERROR)

project(VersaLib)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(pybind11 REQUIRED)
find_package(VTK REQUIRED)
find_package(Catch2 REQUIRED)

include(${VTK_USE_FILE})

include(${CMAKE_SOURCE_DIR}/versalib/CMakeLists.txt)

pybind11_add_module(VersaLib ${SRC_FILES} ${LIB_SRC_WRAP} ${HEADER_FILES})

target_link_libraries(VersaLib PUBLIC ${VTK_LIBRARIES})
target_include_directories(VersaLib PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/versalib/include) 

