#include "catch2/catch.hpp"

#include "VoxelizerFilter.h"
#include "vtkSphereSource.h"
#include "VoxelizerFilter.h"
#include "VoxShelling.h"
#include "vtkImageData.h"
#include "vtkXMLImageDataWriter.h"
#include "vtkSmartPointer.h"

TEST_CASE("voxelize polydata", "[Process]")
{
    std::string outPath_2("./test/test_output/sphere_hollow.vti");

    vtkSmartPointer<vtkSphereSource> sphereSource =
        vtkSmartPointer<vtkSphereSource>::New();
    sphereSource->SetRadius(20);
    sphereSource->SetPhiResolution(30);
    sphereSource->SetThetaResolution(30);
    vtkSmartPointer<vtkPolyData> pd = sphereSource->GetOutput();
    sphereSource->Update();

    vtkNew<VoxelizerFilter> voxF;
    voxF->SetInputData(pd);
    voxF->Update();

    vtkNew<VoxShelling> voxS;
    voxS->SetInputConnection(voxF->GetOutputPort());
    voxS->Update();

    vtkSmartPointer<vtkXMLImageDataWriter> writer3 =
        vtkSmartPointer<vtkXMLImageDataWriter>::New();
    writer3->SetFileName(outPath_2.c_str());

    writer3->SetInputData(voxS->GetOutput());
    writer3->Write();
}