set(
    LIB_SRC_WRAP
    src/VersaLibWrapper.cc
)

set(
    LIB_HEADER_WRAP
    include/PybindVTKTypeCaster.h
)

pybind11_add_module(_versalib MODULE
  ${LIB_HEADER_WRAP}
  ${LIB_SRC_WRAP}
)

target_include_directories(_versalib PRIVATE include)
target_link_libraries(_versalib PRIVATE ${VTK_LIBRARIES} VersaLib)
install(TARGETS _versalib DESTINATION .)