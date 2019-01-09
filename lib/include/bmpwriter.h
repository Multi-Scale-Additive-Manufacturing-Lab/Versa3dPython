#ifndef BMPWRITER_H
#define BMPWRITER_H

#include <vtkImageData.h>
#include <vtkWeakPointer.h>

class bmpwriter
{
    private:
        vtkWeakPointer<vtkImageData> data;
        FILE* bmp_file;
        int dpm[2] = {23623, 23623};

        unsigned char* create_bmp_file_header(int height, int width, int file_size, int a_offset);
        unsigned char* create_bmp_info_header(int height, int width, int dib_header_size, int a_size, int dpm[]);
        void init_header(int w, int h, int array_size);

    public:
        bmpwriter(const char *file_path, vtkImageData *img);
        void write_to_file();
};

#endif