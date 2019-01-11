#include "bmpwriter.h"
#include <iostream>
#include "EasyBMP.h"

using namespace std;

bmpwriter::bmpwriter(const char *file_path, vtkImageData *img)
{
	this->file_path = file_path;
	this->data = img;
}

void bmpwriter::write_to_file()
{
	BMP img;
	int *dim = this->data->GetDimensions();
	img.SetSize(dim[0],dim[1]);
	img.SetBitDepth(1);

	int *extent = this->data->GetExtent();

	for(int j = extent[3];j >= extent[2];j--)
	{
		for(int i = extent[0]; i <= extent[1]; i++)
		{
			int p_j = extent[3]-j;
			int p_i = i-extent[0];
			float val =  this->data->GetScalarComponentAsFloat(i, j, 0, 0);
			if(val == 255)
			{
				img(p_i,p_j)->Red = 255;
				img(p_i,p_j)->Green = 255;
				img(p_i,p_j)->Blue = 255;

			}else
			{
				img(p_i,p_j)->Red = 0;
				img(p_i,p_j)->Green = 0;
				img(p_i,p_j)->Blue = 0;
			}
		}
	}
	
	img.WriteToFile(this->file_path);

}
