#include "bmpwriter.h"

bmpwriter::bmpwriter()
{

}
/*
void bmpwriter::set_input(vtkImageData * img)
{
	cout<<"hello world"<<endl;
}
*/
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
		.def("write_to_file",&bmpwriter::write_to_file)
	;
}