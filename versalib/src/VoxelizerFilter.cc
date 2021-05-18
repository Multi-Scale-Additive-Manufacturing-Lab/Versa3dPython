/*
 * File: VoxelizerFilter.cc
 * Project: Versa3d
 * File Created: 2021-05-03
 * Author: Marc Wang (marc.wang@uwaterloo.ca)
 * -----
 * Last Modified: 2021-05-03
 * Modified By: Marc Wang (marc.wang@uwaterloo.ca>)
 * -----
 * Copyright (c) 2021 Marc Wang. All rights reserved. 
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 * 
 * 1. Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer. 
 * 
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution. 
 * 
 * 3. Neither the name of the copyright holder nor the names of its contributors
 * may be used to endorse or promote products derived from this software without
 * specific prior written permission.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#include "VoxelizerFilter.h"
#include "vtkObjectFactory.h"
#include "vtkPolyData.h"
#include "vtkImageData.h"
#include "vtkDataArray.h"
#include "vtkPointData.h"
#include "vtkNew.h"
#include "vtkImageStencil.h"
#include "vtkPolyDataToImageStencil.h"
#include "vtkStreamingDemandDrivenPipeline.h"

vtkStandardNewMacro(VoxelizerFilter);

VoxelizerFilter::VoxelizerFilter()
{
    this->ScalarType = VTK_UNSIGNED_CHAR;
    this->ForegroundValue = 255;
    this->BackgroundValue = 0;

    this->ModelBounds[0] = 0.0;
    this->ModelBounds[1] = 0.0;
    this->ModelBounds[2] = 0.0;
    this->ModelBounds[3] = 0.0;
    this->ModelBounds[4] = 0.0;
    this->ModelBounds[5] = 0.0;

    this->SampleDimensions[0] = 50;
    this->SampleDimensions[1] = 50;
    this->SampleDimensions[2] = 50;

    this->Dpi[0] = 600;
    this->Dpi[1] = 600;
    this->Dpi[2] = 600;
}

int VoxelizerFilter::RequestInformation(vtkInformation *vtkNotUsed(request),
                                        vtkInformationVector **inputVector, vtkInformationVector *outputVector)
{
    vtkInformation *outInfo = outputVector->GetInformationObject(0);

    vtkInformation *inInfo = inputVector[0]->GetInformationObject(0);
    vtkPolyData *input = vtkPolyData::GetData(inInfo);

    input->GetBounds(this->ModelBounds);
    double origin[3];
    double spacing[3];

    for (int i = 0; i < 3; i++)
    {
        spacing[i] = 25.4 / this->Dpi[i];
        origin[i] = this->ModelBounds[2 * i] + spacing[i] / 2;
        this->SampleDimensions[i] = static_cast<int>(ceil((this->ModelBounds[2 * i + 1] - this->ModelBounds[2 * i]) / spacing[i]));
    }

    outInfo->Set(vtkDataObject::ORIGIN(), origin, 3);
    outInfo->Set(vtkDataObject::SPACING(), spacing, 3);
    outInfo->Set(vtkStreamingDemandDrivenPipeline::WHOLE_EXTENT(), 0, this->SampleDimensions[0] - 1,
                 0, this->SampleDimensions[1] - 1, 0, this->SampleDimensions[2] - 1);
    vtkDataObject::SetPointDataActiveScalarInfo(outInfo, this->ScalarType, 1);
    return 1;
}

int VoxelizerFilter::RequestData(vtkInformation *vtkNotUsed(request),
                                 vtkInformationVector **inputVector, vtkInformationVector *outputVector)
{
    // get the input
    vtkInformation *inInfo = inputVector[0]->GetInformationObject(0);
    vtkPolyData *input = vtkPolyData::GetData(inInfo);

    // get the output
    vtkInformation *outInfo = outputVector->GetInformationObject(0);
    vtkImageData *output = vtkImageData::GetData(outInfo);

    int ext[6];
    outInfo->Get(vtkStreamingDemandDrivenPipeline::WHOLE_EXTENT(), ext);

    double origin[3];
    double spacing[3];
    outInfo->Get(vtkDataObject::ORIGIN(), origin);
    outInfo->Get(vtkDataObject::SPACING(), spacing);

    vtkNew<vtkImageData> bgIm;
    bgIm->SetDimensions(this->SampleDimensions);
    bgIm->SetOrigin(origin);
    bgIm->SetExtent(ext);
    bgIm->AllocateScalars(outInfo);
    bgIm->SetSpacing(spacing);
    bgIm->GetPointData()->GetScalars()->Fill(this->ForegroundValue);

    vtkNew<vtkPolyDataToImageStencil> PolySten;
    PolySten->SetInputData(input);
    PolySten->SetOutputOrigin(origin);
    PolySten->SetOutputSpacing(spacing);
    PolySten->SetOutputWholeExtent(ext);
    PolySten->Update();

    vtkNew<vtkImageStencil> Sten;
    Sten->SetInputData(bgIm);
    Sten->SetStencilConnection(PolySten->GetOutputPort());
    Sten->SetBackgroundValue(this->BackgroundValue);
    Sten->ReverseStencilOff();
    Sten->Update();

    output->ShallowCopy(Sten->GetOutput());
    return 1;
}

int VoxelizerFilter::FillInputPortInformation(int vtkNotUsed(port), vtkInformation *info)
{
    info->Set(vtkAlgorithm::INPUT_REQUIRED_DATA_TYPE(), "vtkPolyData");
    return 1;
}

void VoxelizerFilter::PrintSelf(ostream &os, vtkIndent indent)
{
    this->Superclass::PrintSelf(os, indent);
}