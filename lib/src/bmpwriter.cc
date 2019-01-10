#include "bmpwriter.h"
#include <iostream>
#include <errno.h>
#include <fstream>
#include <bitset>

using namespace std;

bmpwriter::bmpwriter(const char *file_path, vtkImageData *img)
{
	errno_t err;
	if( (err = fopen_s(&this->bmp_file,file_path, "wb")) != 0)
	{
		fprintf(stderr, "cannot open file '%s': %s\n",
            file_path, strerror(err));
	}
	this->data = img;
}

unsigned char* bmpwriter::create_bmp_file_header(int height, int width, int file_size, int a_offset){

    static unsigned char fileHeader[] = {
        0,0, /// signature
        0,0,0,0, /// image file size in bytes
        0,0,0,0, /// reserved
        0,0,0,0, /// start of pixel array
    };

    fileHeader[ 0] = (unsigned char)('B');
    fileHeader[ 1] = (unsigned char)('M');
    fileHeader[ 2] = (unsigned char)(file_size    );
    fileHeader[ 3] = (unsigned char)(file_size>> 8);
    fileHeader[ 4] = (unsigned char)(file_size>>16);
    fileHeader[ 5] = (unsigned char)(file_size>>24);
    fileHeader[10] = (unsigned char)(a_offset);

    return fileHeader;
}

unsigned char* bmpwriter::create_bmp_info_header(int height, int width, int dib_header_size, int a_size, int dpm[]){
    static unsigned char infoHeader[] = {
        0,0,0,0, /// header size
        0,0,0,0, /// image width
        0,0,0,0, /// image height
        0,0, /// number of color planes
        0,0, /// bits per pixel
        0,0,0,0, /// compression
        0,0,0,0, /// image size
        0,0,0,0, /// horizontal resolution
        0,0,0,0, /// vertical resolution
        0,0,0,0, /// colors in color table
        0,0,0,0, /// important color count
    };

    infoHeader[ 0] = (unsigned char)(dib_header_size);
    infoHeader[ 4] = (unsigned char)(width    );
    infoHeader[ 5] = (unsigned char)(width>> 8);
    infoHeader[ 6] = (unsigned char)(width>>16);
    infoHeader[ 7] = (unsigned char)(width>>24);
    infoHeader[ 8] = (unsigned char)(height    );
    infoHeader[ 9] = (unsigned char)(height>> 8);
    infoHeader[10] = (unsigned char)(height>>16);
    infoHeader[11] = (unsigned char)(height>>24);
    infoHeader[12] = (unsigned char)(1);
    infoHeader[14] = (unsigned char)(1);

	infoHeader[20] = (unsigned char)(a_size);
	infoHeader[21] = (unsigned char)(a_size>>8);
	infoHeader[22] = (unsigned char)(a_size>>16);
	infoHeader[23] = (unsigned char)(a_size>>24);

	for(int i = 0; i < 2 ; i++)
	{
		infoHeader[24+i*4] = (unsigned char)(dpm[i]);
		infoHeader[25+i*4] = (unsigned char)(dpm[i]>>8);
		infoHeader[26+i*4] = (unsigned char)(dpm[i]>>16);
		infoHeader[27+i*4] = (unsigned char)(dpm[i]>>24);
	}

    return infoHeader;
}

void bmpwriter::init_header(int w, int h, int array_size)
{
	int bmp_header_size = 14;
	int dib_header_size = 40;
	int rgb_color_table = 8;

	int a_offet = bmp_header_size + dib_header_size + rgb_color_table;
	int total_size = bmp_header_size + dib_header_size + array_size + rgb_color_table;

	unsigned char* file_header = this->create_bmp_file_header(w, h, total_size, a_offet);
	unsigned char* info_header = this->create_bmp_info_header(h,w,dib_header_size,array_size,this->dpm);
	fwrite(file_header,1, bmp_header_size, this->bmp_file);
	fwrite(info_header,1, dib_header_size, this->bmp_file);

	static unsigned char color_table_black[] = {255,255,255,255};
	static unsigned char color_table_white[] = {0,0,0,0};

	fwrite(color_table_black,1,4,this->bmp_file);
	fwrite(color_table_white,1,4,this->bmp_file);
}

void bmpwriter::write_to_file()
{
	int *dim = this->data->GetDimensions();
	int line_size = dim[0];
	int padding = 32 - dim[0] % 32;

	int total_line_size = (line_size + padding)/8;

	this->init_header(dim[0], dim[1], total_line_size*dim[1]);

	std::bitset<32> b;
	int *extent = this->data->GetExtent();
	int bit_loc = 0;
	for(int j = extent[3]; j>=extent[2]; j--)
	{
		for(int i = extent[0]; i<= extent[1]; i++)
		{
			float val =  this->data->GetScalarComponentAsFloat(i, j, 0, 0);
			if(val == 255.0)
			{
				b.set(bit_loc, false);
			}else
			{
				b.set(bit_loc, true);
			}
			bit_loc++;

			if(bit_loc == 32)
			{
				unsigned long temp = b.to_ulong();
				bit_loc = 0;
				fwrite(reinterpret_cast<unsigned char*>(&temp), 1,4,this->bmp_file);
				b.reset();
			}
		}

		unsigned long temp = b.to_ulong();
		fwrite(reinterpret_cast<unsigned char*>(&temp), 1,4,this->bmp_file);
		b.reset();
		bit_loc = 0;
	}

	fclose(this->bmp_file);
}
