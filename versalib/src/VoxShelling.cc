#include "VoxShelling.h"
#include "vtkObjectFactory.h"
#include "vtkNew.h"
#include "vtkImageData.h"
#include "vtkExtractVOI.h"
#include "vtkImageEuclideanDistance.h"
#include "vtkImageThreshold.h"
#include "vtkImageShiftScale.h"
#include "vtkImageMask.h"
#include "vtkStreamingDemandDrivenPipeline.h"

vtkStandardNewMacro(VoxShelling);

VoxShelling::VoxShelling()
{
    this->ContourThickness = 0.1;
    this->InFill = 0.8;
}

int VoxShelling::RequestInformation(vtkInformation *vtkNotUsed(request),
                                    vtkInformationVector **inputVector, vtkInformationVector *outputVector)
{
    vtkInformation *outInfo = outputVector->GetInformationObject(0);
    vtkInformation *inInfo = inputVector[0]->GetInformationObject(0);

    vtkImageData *input = vtkImageData::GetData(inInfo);

    outInfo->Set(vtkDataObject::ORIGIN(), input->GetOrigin(), 3);
    outInfo->Set(vtkDataObject::SPACING(), input->GetSpacing(), 3);
    outInfo->Set(vtkStreamingDemandDrivenPipeline::WHOLE_EXTENT(), input->GetExtent(), 6);

    return 1;
}

int VoxShelling::RequestData(vtkInformation *vtkNotUsed(request),
                                 vtkInformationVector **inputVector, vtkInformationVector *outputVector)
{
    vtkInformation *inInfo = inputVector[0]->GetInformationObject(0);
    vtkImageData *input = vtkImageData::GetData(inInfo);

    // get the output
    vtkInformation *outInfo = outputVector->GetInformationObject(0);
    vtkImageData *output = vtkImageData::GetData(outInfo);

    int ext[6];
    outInfo->Get(vtkStreamingDemandDrivenPipeline::WHOLE_EXTENT(), ext);

    double origin[3];
    double spacing[3];
    outInfo->Get(vtkDataObject::ORIGIN(), origin);
    outInfo->Get(vtkDataObject::SPACING(), spacing);

    output->AllocateScalars(VTK_DOUBLE, 1);
    output->SetOrigin(origin);
    output->SetSpacing(spacing);
    output->SetExtent(ext);

    vtkNew<vtkExtractVOI> voi;
    voi->SetSampleRate(1, 1, 1);
    voi->SetInputData(input);

    vtkNew<vtkImageEuclideanDistance> t_edt;
    t_edt->SetInputConnection(voi->GetOutputPort());
    t_edt->InitializeOn();

    double pix_offset = this->ContourThickness / spacing[2];

    vtkNew<vtkImageThreshold> SkinImg;
    SkinImg->ThresholdBetween(0, pix_offset);
    SkinImg->SetOutputScalarTypeToDouble();
    SkinImg->SetInValue(1.0);
    SkinImg->SetOutValue(0);
    SkinImg->SetInputConnection(t_edt->GetOutputPort());

    for (auto z = ext[4]; z < ext[5]; ++z)
    {
        int select[6] = {ext[0], ext[1], ext[2], ext[3], z, z};
        voi->SetVOI(select);
        voi->Update();
        
        t_edt->Update();
        SkinImg->Update();

        output->CopyAndCastFrom(SkinImg->GetOutput(), select);
    }

    return 1;
}
int VoxShelling::FillInputPortInformation(int vtkNotUsed(port), vtkInformation *info)
{
    info->Set(vtkImageAlgorithm::INPUT_REQUIRED_DATA_TYPE(), "vtkImageData");
    return 1;
}

void VoxShelling::PrintSelf(ostream &os, vtkIndent indent)
{
    this->Superclass::PrintSelf(os, indent);
}