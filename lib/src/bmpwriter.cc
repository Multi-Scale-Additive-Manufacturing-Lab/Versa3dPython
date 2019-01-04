#include "bmpwriter.h"
#include "PybindVTKTypeCaster.h"

using namespace std;

namespace py = pybind11;

PYBIND11_VTK_TYPECASTER(vtkImageData)
PYBIND11_DECLARE_HOLDER_TYPE(T, std::shared_ptr<T>);

bmpwriter::bmpwriter()
{

}

void bmpwriter::set_input(vtkImageData * img)
{
	cout<<"hello world"<<endl;
}

void bmpwriter::write_to_file()
{
	cout<<"hello world"<<endl;
}

//
// Create Python Module, with converters and MyClass wrapped
//
PYBIND11_MODULE(Versa3dLib, m)
{
	py::class_<bmpwriter>(m,"bmpwriter")
		.def(py::init<>())
		.def("set_input",&bmpwriter::set_input)
		.def("write_to_file",&bmpwriter::write_to_file)
	;
}