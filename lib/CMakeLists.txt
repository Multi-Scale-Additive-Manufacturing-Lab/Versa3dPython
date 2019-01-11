cmake_minimum_required(VERSION 3.5)

set(LIB_SRC
    ${CMAKE_CURRENT_SOURCE_DIR}/src/bmpwriter.cc
    ${CMAKE_CURRENT_SOURCE_DIR}/src/EasyBMP.cpp
)

set(LIB_SRC_WRAP
    ${CMAKE_CURRENT_SOURCE_DIR}/src/bmpwriter_wrap.cc
)

pybind11_add_module(Versa3dLib ${LIB_SRC} ${LIB_SRC_WRAP})
#message(${VTK_LIBRARIES})

#in conda-forge vtk pkg, HDF5 dependencies path are hard coded
#target_link_libraries(Versa3lib PRIVATE ${VTK_LIBRARIES}) Fails
target_link_libraries(Versa3dLib PUBLIC ${VTK_COMPONENT})
target_include_directories(Versa3dLib PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include) 

######### TEST #############
SET(TEST_DIR ${CMAKE_SOURCE_DIR}/test)
SET(TEST_SRC ${TEST_DIR}/test_bmpwriter.cc)

add_executable(Versa3dLibtest ${TEST_SRC} ${LIB_SRC})
target_include_directories(Versa3dLibtest PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include) 
target_link_libraries(Versa3dLibtest gtest gtest_main ${VTK_COMPONENT})

add_test(NAME Versa3dLibTest COMMAND RunUnitTest)