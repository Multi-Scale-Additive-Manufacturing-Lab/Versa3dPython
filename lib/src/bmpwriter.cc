#include "bmpwriter.h"
#include <iostream>
#include "EasyBMP.h"

enum _diffusion_map
{
	floyd_steinberg
};

bmpwriter::bmpwriter(const char *file_path, vtkImageData *img)
{
	this->file_path = file_path;
	this->data->DeepCopy(img);

	this->dither_map = floyd_steinberg;
	this->diffusion_map[floyd_steinberg] = {
		{1, 0, 7.0 / 16.0},
		{-1, 1, 3.0 / 16.0},
		{0, 1, 5.0 / 16.0},
		{1, 1, 1.0 / 16.0}};
}

void bmpwriter::propagate_error(int i, int j, float error)
{
	float old_val = this->data->GetScalarComponentAsFloat(i, j, 0, 0);
	float new_val = old_val + error;
	this->data->SetScalarComponentFromFloat(i, j, 0, 0, new_val);
}

float bmpwriter::find_closest_color(float val)
{
	if (val <= 0)
	{
		return 0;
	}
	else if (val >= 255)
	{
		return 255;
	}
	else
	{
		return round(val / 255) * 255;
	}
}

float bmpwriter::dither(int i, int j)
{
	float val = this->data->GetScalarComponentAsFloat(i, j, 0, 0);
	float new_val = this->find_closest_color(val);
	float error = val - new_val;

	if (error != 0)
	{
		auto map = this->diffusion_map[this->dither_map];
		int *extent = this->data->GetExtent();
		this->data->SetScalarComponentFromFloat(i, j, 0, 0, new_val);
		for (auto it = map.begin(); it < map.end(); it++)
		{
			vector<float> cell = *it;
			int di = i + cell[0];
			int dj = j + cell[1];
			float derror = cell[2];
			if ((extent[0] <= di && di <= extent[1]) && (extent[2] <= dj && dj <= extent[3]))
			{
				this->propagate_error(di, dj, derror * error);
			}
		}
		return new_val;
	}

	return val;
}

void bmpwriter::write_to_file()
{
	BMP img;
	int *dim = this->data->GetDimensions();
	img.SetSize(dim[0], dim[1]);
	img.SetBitDepth(1);

	int *extent = this->data->GetExtent();

	for (int j = extent[3]; j >= extent[2]; j--)
	{
		for (int i = extent[0]; i <= extent[1]; i++)
		{
			int p_j = extent[3] - j;
			int p_i = i - extent[0];
			float val = this->dither(i, j);
			if (val == 255)
			{
				img(p_i, p_j)->Red = 255;
				img(p_i, p_j)->Green = 255;
				img(p_i, p_j)->Blue = 255;
			}
			else
			{
				img(p_i, p_j)->Red = 0;
				img(p_i, p_j)->Green = 0;
				img(p_i, p_j)->Blue = 0;
			}
		}
	}

	img.WriteToFile(this->file_path);
}
