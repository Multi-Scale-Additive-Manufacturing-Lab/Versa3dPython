set(
    LIB_SRC_WRAP
    src/VersaLib_wrapper.cc
)

set(
    LIB_HEADER_WRAP
    include/PybindVTKTypeCaster.h
)

pybind11_add_module(VersaLibPython MODULE
  ${LIB_HEADER_WRAP}
  ${LIB_SRC_WRAP}
)

target_link_libraries(VersaLibPython VersaLib::VersaFilters ${VTK_LIBRARIES})