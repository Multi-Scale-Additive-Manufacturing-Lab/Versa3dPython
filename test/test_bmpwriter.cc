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
            white_img->SetSpacing(0.04,0.04,0.01);
            white_img->SetDimensions(20,20,1);
            white_img->AllocateScalars(VTK_FLOAT, 1);
            vtkWeakPointer<vtkPointData> vtk_point_data = white_img->GetPointData();
            vtkWeakPointer<vtkDataArray> array = vtk_point_data->GetScalars();
            array->Fill(255);
        }

        vtkNew<vtkImageData> white_img;
};

TEST_F(bmpwriterTest, print_white)
{
    char path[] = "./test/testOutput/bmpwriter_output"; 
    unique_ptr<bmpwriter> writer = make_unique<bmpwriter>(path,white_img);
    writer->write_to_file();
}