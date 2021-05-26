
set(SRC_FILES 
    src/VoxDithering.cc
    src/VoxelizerFilter.cc
    src/VoxShelling.cc
)

set(HEADER_FILES
    include/VoxDithering.h
    include/VoxelizerFilter.h
    include/VoxShelling.h
)

add_library(VersaLib ${SRC_FILES} ${HEADER_FILES})
target_link_libraries(VersaLib ${VTK_LIBRARIES})
target_include_directories(VersaLib PUBLIC include)