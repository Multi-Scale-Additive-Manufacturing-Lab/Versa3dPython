#include "gtest/gtest.h"
#include "vtkNew.h"
#include <vtkWeakPointer.h>
#include <vtkImageData.h>
#include <vtkPointData.h>
#include <vtkDataArray.h>
#include "bmpwriter.h"

using namespace std;

class bmpwriterTest : public ::testing::Test
{
    protected:
        void SetUp() override {
            black_img->SetSpacing(0.04,0.04,0.01);
            black_img->SetDimensions(20,20,1);
            black_img->AllocateScalars(VTK_FLOAT, 1);
            vtkWeakPointer<vtkPointData> vtk_point_data = black_img->GetPointData();
            vtkWeakPointer<vtkDataArray> array = vtk_point_data->GetScalars();
            array->Fill(0);
        }

        vtkNew<vtkImageData> black_img;
};

TEST_F(bmpwriterTest, print_white)
{
    char path[] = "./test/testOutput/bmpwriter_output/image.bmp"; 
    unique_ptr<bmpwriter> writer = make_unique<bmpwriter>(path,black_img);
    writer->write_to_file();
}