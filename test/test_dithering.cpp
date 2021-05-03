#include "catch2/catch.hpp"

#include "vtkNew.h"
#include "vtkSTLReader.h"

TEST_CASE("Test Dither image", "[Process]")
{
    std::string path("./test_artifact/3DBenchy.stl");

    vtkNew<vtkSTLReader> reader;
    reader->SetFileName(path.c_str());
    reader->Update();


    
}