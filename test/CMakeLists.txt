SET(TEST_SRC test_voxelization.cpp
             test_main.cpp)

add_executable(VersaLibTest ${TEST_SRC})
target_link_libraries(VersaLibTest PRIVATE Catch2::Catch2 VersaLibCore ${VTK_LIBRARIES})

include(Catch)
catch_discover_tests(VersaLibTest)