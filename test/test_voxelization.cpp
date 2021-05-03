#include "catch2/catch.hpp"

#include "vtkNew.h"
#include "vtkSTLReader.h"
#include "vtkXMLImageDataWriter.h"
#include "VoxelizerFilter.h"

TEST_CASE("voxelize polydata", "[Process]")
{
    std::string inPath("./test_artifact/3DBenchy.stl");
    std::string outPath("./output/3DBenchy.vti");

    vtkNew<vtkSTLReader> reader;
    reader->SetFileName(inPath.c_str());
    reader->Update();

    vtkNew<VoxelizerFilter> voxF;
    voxF->SetDpi(600, 600, 600);
    voxF->Update();

    

    vtkNew<vtkXMLImageDataWriter> imWriter;
    imWriter->SetInputConnection(voxF->GetOutputPort());
    imWriter->SetFileName(outPath.c_str());
    imWriter->Update();
    imWriter->Write();
}