#include "bmpwriter.h"
#include "skeletonizer.h"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "PybindVTKTypeCaster.h"
#include <vtkSmartPointer.h>

namespace py = pybind11;

PYBIND11_MODULE(Versa3dLib, m)
{
	py::class_<bmpwriter>(m, "bmpwriter")
		.def(py::init<vtkImageData *>())
		.def("write_to_file", &bmpwriter::write_to_file,
			 "write vtkImgData to monochrome bmp",
			 py::arg("file_path"))
		.def("split_print", &bmpwriter::split_print,
			 "write vtkImgData to monochrome BMP in imtech compatible size",
			 py::arg("file_path"),
			 py::arg("margin"),
			 py::arg("size_limit"));

	py::class_<skeletonizer>(m, "skeletonizer")
		.def(py::init<vtkPolyData *>())
		.def("get_offset", &skeletonizer::get_offset);
}