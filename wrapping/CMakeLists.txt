set(
    LIB_SRC_WRAP
    src/VersaLibWrapper.cc
)

set(
    LIB_HEADER_WRAP
    include/PybindVTKTypeCaster.h
)

pybind11_add_module(_versalib_wrapped MODULE
  ${LIB_HEADER_WRAP}
  ${LIB_SRC_WRAP}
)

target_include_directories(_versalib_wrapped PRIVATE include)
target_link_libraries(_versalib_wrapped PRIVATE ${VTK_LIBRARIES} VersaLib)
install(TARGETS _versalib_wrapped DESTINATION .)