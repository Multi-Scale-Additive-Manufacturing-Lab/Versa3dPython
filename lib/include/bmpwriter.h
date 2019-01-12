#ifndef BMPWRITER_H
#define BMPWRITER_H

#include <vtkImageData.h>
#include <vtkNew.h>
#include <map>
#include <vector>

using namespace std;

class bmpwriter
{
    private:
        map<int,vector<vector<float>>> diffusion_map;
        vtkNew<vtkImageData> data;
        const char *file_path;
        float dither(int i,int j);
        int dither_map;
        float find_closest_color(float val);
        void propagate_error(int i,int j,float error);

    public:
        bmpwriter(const char *file_path, vtkImageData *img);
        void write_to_file();
};

#endif