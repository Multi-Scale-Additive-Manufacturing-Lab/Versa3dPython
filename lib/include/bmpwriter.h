#ifndef BMPWRITER_H
#define BMPWRITER_H

#include <pybind11/pybind11.h>
#include <vtkImageData.h>

class bmpwriter
{
    private:
        vtkImageData* data;

    public:
        bmpwriter();
        void set_input(vtkImageData * img);
        void write_to_file();
};

#endif