#include "bmpwriter.h"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "PybindVTKTypeCaster.h"

namespace py = pybind11;

PYBIND11_VTK_TYPECASTER(vtkImageData)

PYBIND11_MODULE(Versa3dLib, m)
{
	py::class_<bmpwriter>(m,"bmpwriter")
		.def(py::init<vtkImageData *>())
		.def("write_to_file",&bmpwriter::write_to_file)
		.def("split_print",&bmpwriter::split_print)
	;
}