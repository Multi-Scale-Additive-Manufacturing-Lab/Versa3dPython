SET(TEST_DIR ${CMAKE_CURRENT_SOURCE_DIR}/test)
SET(TEST_SRC ${TEST_DIR}/test_voxelization.cpp
             ${TEST_DIR}/test_main.cpp)

add_executable(VersaLibTest ${TEST_SRC})
target_link_libraries(VersaLibTest Catch2::Catch2 VersaLibCore)

include(CTest)
include(Catch)

catch_discover_tests(VersaLibTest)