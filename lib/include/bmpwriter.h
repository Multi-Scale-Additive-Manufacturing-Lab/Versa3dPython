#include <pybind11/pybind11.h>
#include <vtkImageData.h>

using namespace std;

namespace py = pybind11;

class bmpwriter
{
    private:
        vtkImageData* data;

    public:
        bmpwriter();
        //void set_input(vtkImageData* img);
        void write_to_file();
};