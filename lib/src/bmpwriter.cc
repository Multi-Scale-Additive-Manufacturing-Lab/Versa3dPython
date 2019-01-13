#include "bmpwriter.h"
#include <iostream>
#include "EasyBMP.h"

enum _diffusion_map : int
{
	floyd_steinberg,
	atkinson,
	jarvis_judice_ninke,
	stucki,
	burkes,
	sierra3,
	sierra2,
	sierra2_4a,
	stevenson_arce
};

bmpwriter::bmpwriter(vtkImageData *img)
{
	this->data->DeepCopy(img);

	this->dither_map = floyd_steinberg;
	this->diffusion_map[floyd_steinberg] = {
		{1, 0, 7.0 / 16.0},
		{-1, 1, 3.0 / 16.0},
		{0, 1, 5.0 / 16.0},
		{1, 1, 1.0 / 16.0}};
	this->diffusion_map[atkinson] = {
		{1, 0, 1.0 / 18.0},
		{2, 0, 1.0 / 8.0},
		{-1, 1, 1.0 / 8.0},
		{0, 1, 1.0 / 8.0},
		{1, 1, 1.0 / 8.0},
		{0, 2, 1.0 / 8.0}};
	this->diffusion_map[jarvis_judice_ninke] = {
		{1, 0, 7.0 / 48.0},
		{2, 0, 5.0 / 48.0},
		{-2, 1, 3.0 / 48.0},
		{-1, 1, 5.0 / 48.0},
		{0, 1, 7.0 / 48.0},
		{1, 1, 5.0 / 48.0},
		{2, 1, 3.0 / 48.0},
		{-2, 2, 1.0 / 48.0},
		{-1, 2, 3.0 / 48.0},
		{0, 2, 5.0 / 48.0},
		{1, 2, 3.0 / 48.0},
		{2, 2, 1.0 / 48.0}};
	this->diffusion_map[stucki] = {
		{1, 0, 8.0 / 42.0},
		{2, 0, 4.0 / 42.0},
		{-2, 1, 2.0 / 42.0},
		{-1, 1, 4.0 / 42.0},
		{0, 1, 8.0 / 42.0},
		{1, 1, 4.0 / 42.0},
		{2, 1, 2.0 / 42.0},
		{-2, 2, 1.0 / 42.0},
		{-1, 2, 2.0 / 42.0},
		{0, 2, 4.0 / 42.0},
		{1, 2, 2.0 / 42.0},
		{2, 2, 1.0 / 42.0}};
	this->diffusion_map[burkes] = {
		{1, 0, 8.0 / 32.0},
		{2, 0, 4.0 / 32.0},
		{-2, 1, 2.0 / 32.0},
		{-1, 1, 4.0 / 32.0},
		{0, 1, 8.0 / 32.0},
		{1, 1, 4.0 / 32.0},
		{2, 1, 2.0 / 32.0}};
	this->diffusion_map[sierra3] = {
		{1, 0, 5.0 / 32.0},
		{2, 0, 3.0 / 32.0},
		{-2, 1, 2.0 / 32.0},
		{-1, 1, 4.0 / 32.0},
		{0, 1, 5.0 / 32.0},
		{1, 1, 4.0 / 32.0},
		{2, 1, 2.0 / 32.0},
		{-1, 2, 2.0 / 32.0},
		{0, 2, 3.0 / 32.0},
		{1, 2, 2.0 / 32.0}};
	this->diffusion_map[sierra2] = {
		{1, 0, 4.0 / 16.0},
		{2, 0, 3.0 / 16.0},
		{-2, 1, 1.0 / 16.0},
		{-1, 1, 2.0 / 16.0},
		{0, 1, 3.0 / 16.0},
		{1, 1, 2.0 / 16.0},
		{2, 1, 1.0 / 16.0}};
	this->diffusion_map[sierra2_4a] = {
		{1, 0, 2.0 / 4.0},
		{-1, 1, 1.0 / 4.0},
		{0, 1, 1.0 / 4.0}};
	this->diffusion_map[stevenson_arce] = {
		{2, 0, 32.0 / 200.0},
		{-3, 1, 12.0 / 200.0},
		{-1, 1, 26.0 / 200.0},
		{1, 1, 30.0 / 200.0},
		{3, 1, 30.0 / 200.0},
		{-2, 2, 12.0 / 200.0},
		{0, 2, 26.0 / 200.0},
		{2, 2, 12.0 / 200.0},
		{-3, 3, 5.0 / 200.0},
		{-1, 3, 12.0 / 200.0},
		{1, 3, 12.0 / 200.0},
		{3, 3, 5.0 / 200.0}};
}

void bmpwriter::set_dither_map(int map)
{
	this->dither_map = map;
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

void bmpwriter::write_to_file(const char *file_path)
{
	BMP img;
	int *dim = this->data->GetDimensions();
	img.SetSize(dim[0], dim[1]);
	img.SetBitDepth(1);

	int *extent = this->data->GetExtent();

	for (int j = extent[2]; j <= extent[3]; j++)
	{
		for (int i = extent[1]; i >= extent[0]; i--)
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

	img.WriteToFile(file_path);
}

const vector<int> & bmpwriter::split_print(const char *file_path,int margin, int size_limit)
{
	int *dim = this->data->GetDimensions();
	int *extent = this->data->GetExtent();
	vector<shared_ptr<BMP>> list_slice;
	vector<int> list_index;

	float max_j_size = (float)(size_limit - 2 * margin);
	float num_slice = ceil(dim[1] / max_j_size);

	int count = 0;
	for (int k = 0; k < num_slice; k++)
	{
		shared_ptr<BMP> slice = make_shared<BMP>();
		slice->SetBitDepth(1);
		slice->SetSize(dim[0], max_j_size);
		for (int j = max_j_size * k; j < max_j_size * k + max_j_size; j++)
		{
			if (j <= extent[3])
			{
				for (int i = extent[1]; i >= extent[0]; i--)
				{
					int p_i = extent[1] - i;
					int p_j = j - max_j_size * k;
					RGBApixel color;
					if (this->dither(i, j) == 0)
					{
						count++;
						color.Red = 0;
						color.Green = 0;
						color.Blue = 0;
					}
					else
					{
						color.Red = 255;
						color.Green = 255;
						color.Blue = 255;
					}
					slice->SetPixel(p_i,p_j, color);
				}
			}
		}
		if (count != 0)
		{
			list_slice.push_back(slice);
			list_index.push_back(max_j_size * k);
		}
		count = 0;
	}
	
	int non_empty_slice_num = list_slice.size();
	BMP img;
	img.SetBitDepth(1);
	img.SetSize(dim[0] * non_empty_slice_num, size_limit);
	
	for (int l = 0; l < non_empty_slice_num; l++)
	{
		RangedPixelToPixelCopy(*list_slice[l], 0, dim[0] - 1, 0, max_j_size - 1, img, dim[0] * l, margin);
	}
	
	try{
		img.WriteToFile(file_path);
	}catch(exception& e)
	{
		 cout << "Standard exception: " << e.what() << endl;
		 cout << "at file:"<< file_path << endl;
	}
	return list_index;
}