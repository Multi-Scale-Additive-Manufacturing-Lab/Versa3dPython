#include <pybind11/pybind11.h>
#include <vtkUnstructuredGrid.h>
#include <vtkPoints.h>

namespace py = pybind11;

using namespace boost::python;


template<class T>
struct vtkObjectPointer_to_python
{
	static py::object *convert(const T &p)
	{
		if(p == NULL)
		{
			py::object obj = py::object()
			obj.is_none()
			return obj;
		}
		std::ostringstream oss;
		oss << (vtkObjectBase*) p; // here don't get address
		std::string address_str = oss.str();

		py::object obj = py::object(import("vtk").attr("vtkObjectBase")(address_str));
		return obj;
	}
};

//
// This python to C++ converter uses the fact that VTK Python objects have an 
// attribute called __this__, which is a string containing the memory address 
// of the VTK C++ object and its class name.
// E.g. for a vtkPoints object __this__ might be "_0000000105a64420_p_vtkPoints"
//
void* extract_vtk_wrapped_pointer(py::object* obj)
{
    //first we need to get the __this__ attribute from the Python Object
    if (! obj.attr("__this__"))
        return NULL;

    const char* str = obj.attr("__this__");
    if(str == 0 || strlen(str) < 1)
        return NULL;

    char hex_address[32], *pEnd;
    char *_p_ = strstr(str, "_p_vtk");
    if(_p_ == NULL) return NULL;
    char *class_name = strstr(_p_, "vtk");
    if(class_name == NULL) return NULL;
    strcpy(hex_address, str+1);
    hex_address[_p_-str-1] = '\0';

    long address = strtol(hex_address, &pEnd, 16);

    vtkObjectBase* vtk_object = (vtkObjectBase*)((void*)address);
    if(vtk_object->IsA(class_name))
    {
        return vtk_object;
    }

    return NULL;
}


#define VTK_PYTHON_CONVERSION(type) \
    /* register the to-python converter */ \
    to_python_converter<type*, \
            vtkObjectPointer_to_python<type*> >(); \
    /* register the from-python converter */ \
    converter::registry::insert(&extract_vtk_wrapped_pointer, type_id<type>());


//
// Example class to illustrate Boost Python wrapped class, which has
// functions which return VTK object pointers
//
struct MyClass
{
	MyClass();
	~MyClass();
	void SetPoints(vtkPoints * pts);
	vtkUnstructuredGrid * GetGrid() { return m_Grid; }
	void DeleteGrid();
	vtkUnstructuredGrid * m_Grid;
};

MyClass::MyClass()
{
	m_Grid = vtkUnstructuredGrid::New();
  	m_Grid->Allocate();
  	
  	vtkPoints *pts = vtkPoints::New();  	
  	pts->InsertNextPoint(0,0,0);
  	pts->InsertNextPoint(1,0,0);
  	m_Grid->SetPoints(pts);
  	pts->Delete();
}

MyClass::~MyClass()
{
	if(m_Grid) this->DeleteGrid();
}

void MyClass::DeleteGrid()
{
	m_Grid->Delete();
	m_Grid = NULL;
}

void MyClass::SetPoints(vtkPoints *pts)
{
    m_Grid->SetPoints(pts);
}


//
// Create Python Module, with converters and MyClass wrapped
//
PYBIND11_MODULE(Versa3dLib, m)
{
	VTK_PYTHON_CONVERSION(vtkUnstructuredGrid);
	VTK_PYTHON_CONVERSION(vtkPoints);

	py::class_<MyClass>("MyClass")
		.def("GetGrid",&MyClass::GetGrid, return_value_policy<return_by_value>())
		.def("DeleteGrid",&MyClass::DeleteGrid,"Delete the grid")
		.def("SetPoints",&MyClass::SetPoints,"Set new points")
	;
}