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
    map<int, vector<vector<double>>> diffusion_map;
    vtkNew<vtkImageData> data;
    float dither(int i, int j);
    int dither_map;
    float find_closest_color(float val);
    void propagate_error(int i, int j, double error);

  public:
    bmpwriter(vtkImageData *img);
    void set_dither_map(int map);
    void write_to_file(const char *file_path);
    const vector<int> &split_print(const char *file_path,int margin, int size_limit);
};

#endif