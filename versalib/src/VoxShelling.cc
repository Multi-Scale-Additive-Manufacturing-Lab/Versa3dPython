#include "VoxShelling.h"
#include "vtkObjectFactory.h"
#include "vtkNew.h"
#include "vtkImageData.h"
#include "vtkExtractVOI.h"
#include "vtkImageEuclideanDistance.h"
#include "vtkImageThreshold.h"
#include "vtkImageMask.h"
#include "vtkImageAccumulate.h"
#include "vtkImageIterator.h"
#include "vtkImageProgressIterator.h"

vtkStandardNewMacro(VoxShelling);

VoxShelling::VoxShelling()
{
    this->ContourThickness = 0.2;
    this->InFill = 0.8;

    this->SplitPathLength = 1;

}

int VoxShelling::RequestInformation(vtkInformation *vtkNotUsed(request),
                                    vtkInformationVector **inputVector, vtkInformationVector *outputVector)
{
    vtkInformation *outInfo = outputVector->GetInformationObject(0);
    vtkInformation *inInfo = inputVector[0]->GetInformationObject(0);

    vtkImageData *input = vtkImageData::GetData(inInfo);

    double *spacing = input->GetSpacing();

    if (this->SplitMode != SLAB)
    {
        vtkErrorMacro("only slab mode supported");
        return 0;
    }

    if (input->GetScalarType() != VTK_UNSIGNED_CHAR)
    {
        vtkErrorMacro("input image not unsigned_char");
        return 0;
    }
    else
    {
        vtkDataObject::SetPointDataActiveScalarInfo(outInfo, VTK_FLOAT, 1);
    }
    return 1;
}

void VoxShelling::ExecuteShelling(vtkImageData *inData, vtkImageData *outData, int outExt[6], int id)
{
    vtkNew<vtkExtractVOI> voi;
    voi->SetSampleRate(1, 1, 1);
    voi->SetInputData(inData);
    voi->SetVOI(outExt);
    voi->Update();

    vtkNew<vtkImageEuclideanDistance> edt;
    edt->SetInputConnection(voi->GetOutputPort());
    edt->InitializeOn();
    edt->Update();

    vtkNew<vtkImageAccumulate> findMax;
    findMax->SetInputConnection(edt->GetOutputPort());
    findMax->Update();

    double *peak = findMax->GetMax();

    vtkNew<vtkImageThreshold> SkinImg;
    SkinImg->ThresholdByUpper(peak[0]*this->ContourThickness);
    SkinImg->SetOutputScalarTypeToFloat();
    SkinImg->SetInValue(this->InFill);
    SkinImg->SetOutValue(1.0);
    SkinImg->SetInputConnection(edt->GetOutputPort());
    SkinImg->Update();

    vtkNew<vtkImageMask> mask;
    mask->SetImageInputData(SkinImg->GetOutput());
    mask->SetMaskInputData(voi->GetOutput());
    mask->SetMaskedOutputValue(0.0);
    mask->Update();

    vtkImageData *result = mask->GetOutput();
    vtkImageIterator<float> inIt(result, result->GetExtent());
    vtkImageProgressIterator<float> outIt(outData, outExt, this, id);

    while(!inIt.IsAtEnd()){
        float *inSI = inIt.BeginSpan();
        float *outSI = outIt.BeginSpan();
        float *outSIEnd = outIt.EndSpan();

        do{
            ++inSI;
            ++outSI;
            *outSI = *inSI;
        }while(outSI != outSIEnd);

        inIt.NextSpan();
        outIt.NextSpan();
    }

}

void VoxShelling::ThreadedRequestData(vtkInformation *vtkNotUsed(request),
                                      vtkInformationVector **vtkNotUsed(inputVector), vtkInformationVector *vtkNotUsed(outputVector),
                                      vtkImageData ***inData, vtkImageData **outData, int outExt[6], int id)
{
    this->ExecuteShelling(inData[0][0], outData[0], outExt, id);
}

void VoxShelling::PrintSelf(ostream &os, vtkIndent indent)
{
    this->Superclass::PrintSelf(os, indent);
}