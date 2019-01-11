#ifndef BMPWRITER_H
#define BMPWRITER_H

#include <vtkImageData.h>
#include <vtkWeakPointer.h>

class bmpwriter
{
    private:
        vtkWeakPointer<vtkImageData> data;
        const char *file_path;

    public:
        bmpwriter(const char *file_path, vtkImageData *img);
        void write_to_file();
};

#endif