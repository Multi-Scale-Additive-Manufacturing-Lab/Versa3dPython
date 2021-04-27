#include "VoxDithering.h"

#include "vtkInformation.h"
#include "vtkInformationVector.h"
#include "vtkStreamingDemandDrivenPipeline.h"

VoxDithering::VoxDithering()
{
}

int VoxDithering::RequestInformation(vtkInformation *vtkNotUsed(request),
                                     vtkInformationVector **vtkNotUsed(inputVector), vtkInformationVector *outputVector)
{
    return 1;
}

int VoxDithering::RequestData(vtkInformation *vtkNotUsed(request),
                              vtkInformationVector **inputVector, vtkInformationVector *outputVector)
{
    return 1;
}

int VoxDithering::FillInputPortInformation(int vtkNotUsed(port), vtkInformation *info)
{
    info->Set(vtkAlgorithm::INPUT_REQUIRED_DATA_TYPE(), "vtkDataSet");
    return 1;
}

void VoxDithering::PrintSelf(ostream& os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os, indent);
}