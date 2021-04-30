/*
 * File: VoxDithering.cc
 * Project: Versa3d
 * File Created: 2021-04-30
 * Author: Marc Wang (marc.wang@uwaterloo.ca)
 * -----
 * Last Modified: 2021-04-30
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

#include "VoxDithering.h"
#include <math.h>

#include "vtkInformation.h"
#include "vtkInformationVector.h"
#include "vtkStreamingDemandDrivenPipeline.h"
#include "vtkImageData.h"

VoxDithering::VoxDithering()
{
    this->Dithering = VoxDithering::DitheringType::floyd_steinberg;
}

int VoxDithering::RequestInformation(vtkInformation *vtkNotUsed(request),
                                     vtkInformationVector **inputVector, vtkInformationVector *outputVector)
{
    vtkInformation *inInfo = inputVector[0]->GetInformationObject(0);
    vtkImageData *inImg = vtkImageData::GetData(inInfo);

    int *ext = inImg->GetExtent();
    vtkInformation *o_info = outputVector->GetInformationObject(0);
    o_info->Set(vtkStreamingDemandDrivenPipeline::WHOLE_EXTENT(), ext, 6);
    return 1;
}

double VoxDithering::ClosestVal(double pixel)
{
    if (pixel <= 0.0)
    {
        return 0.0;
    }
    else if (pixel >= 1.0)
    {
        return 1.0;
    }
    else
    {
        return round(pixel);
    }
}

DitherMap VoxDithering::GetDitherMap(DitheringType type)
{
    DitherMap d_map;
    switch (type)
    {
    case VoxDithering::DitheringType::floyd_steinberg:

        d_map = {{make_pair(0, 1), 7.0 / 16.0},
                 {make_pair(-1, 1), 3.0 / 16.0},
                 {make_pair(0, 1), 5.0 / 16.0},
                 {make_pair(1, 1), 1.0 / 16.0}};
        break;
    case VoxDithering::DitheringType::atkinson:
        d_map = {{make_pair(1, 0), 1.0 / 8.0},
                 {make_pair(2, 1), 1.0 / 8.0},
                 {make_pair(-1, 1), 1.0 / 8.0},
                 {make_pair(0, 1), 1.0 / 8.0},
                 {make_pair(1, 1), 1.0 / 8.0},
                 {make_pair(0, 2), 1.0 / 8.0}};
        break;
    case VoxDithering::DitheringType::jarvis_judice_ninke:
        d_map = {{make_pair(1, 0), 7.0 / 48.0},
                 {make_pair(2, 0), 5.0 / 48.0},
                 {make_pair(-2, 1), 3.0 / 48.0},
                 {make_pair(-1, 1), 5.0 / 48.0},
                 {make_pair(0, 1), 7.0 / 48.0},
                 {make_pair(1, 1), 5.0 / 48.0},
                 {make_pair(2, 1), 3.0 / 48.0},
                 {make_pair(-2, 2), 1.0 / 48.0},
                 {make_pair(-1, 2), 3.0 / 48.0},
                 {make_pair(0, 2), 5.0 / 48.0},
                 {make_pair(1, 2), 3.0 / 48.0},
                 {make_pair(2, 2), 1.0 / 48.0}};
        break;
    case VoxDithering::DitheringType::stucki:
        d_map = {{make_pair(1, 0), 7.0 / 42.0},
                 {make_pair(2, 0), 4.0 / 42.0},
                 {make_pair(-2, 1), 2.0 / 42.0},
                 {make_pair(-1, 1), 4.0 / 42.0},
                 {make_pair(0, 1), 8.0 / 42.0},
                 {make_pair(1, 1), 4.0 / 42.0},
                 {make_pair(2, 1), 2.0 / 42.0},
                 {make_pair(-2, 2), 1.0 / 42.0},
                 {make_pair(-1, 2), 2.0 / 42.0},
                 {make_pair(0, 2), 4.0 / 42.0},
                 {make_pair(1, 2), 2.0 / 42.0},
                 {make_pair(2, 2), 1.0 / 42.0}};
        break;
    case VoxDithering::DitheringType::burkes:
        d_map = {{make_pair(1, 0), 8.0 / 32.0},
                 {make_pair(2, 0), 3.0 / 32.0},
                 {make_pair(-2, 1), 2.0 / 32.0},
                 {make_pair(-1, 1), 4.0 / 32.0},
                 {make_pair(0, 1), 5.0 / 32.0},
                 {make_pair(1, 1), 4.0 / 32.0},
                 {make_pair(2, 1), 2.0 / 32.0},
                 {make_pair(-1, 2), 2.0 / 32.0},
                 {make_pair(0, 2), 3.0 / 32.0},
                 {make_pair(1, 2), 2.0 / 32.0}};
        break;
    case VoxDithering::DitheringType::sierra3:
        d_map = {{make_pair(1, 0), 5.0 / 32.0},
                 {make_pair(2, 0), 3.0 / 32.0},
                 {make_pair(-2, 1), 2.0 / 32.0},
                 {make_pair(-1, 1), 4.0 / 32.0},
                 {make_pair(0, 1), 5.0 / 32.0},
                 {make_pair(1, 1), 4.0 / 32.0},
                 {make_pair(2, 1), 2.0 / 32.0},
                 {make_pair(-1, 2), 2.0 / 32.0},
                 {make_pair(0, 2), 3.0 / 32.0},
                 {make_pair(1, 2), 2.0 / 32.0}};
        break;
    case VoxDithering::DitheringType::sierra2:
        d_map = {{make_pair(1, 0), 4.0 / 16.0},
                 {make_pair(2, 0), 3.0 / 16.0},
                 {make_pair(-2, 1), 1.0 / 16.0},
                 {make_pair(-1, 1), 2.0 / 16.0},
                 {make_pair(0, 1), 3.0 / 16.0},
                 {make_pair(1, 1), 2.0 / 16.0},
                 {make_pair(2, 1), 1.0 / 16.0}};
        break;
    case VoxDithering::DitheringType::sierra2_4a:
        d_map = {{make_pair(1, 0), 2.0 / 4.0},
                 {make_pair(-1, 1), 1.0 / 4.0},
                 {make_pair(0, 1), 1.0 / 4.0}};
        break;
    case VoxDithering::DitheringType::stevenson_arce:
        d_map = {{make_pair(2, 0), 32.0 / 200.0},
                 {make_pair(-3, 1), 12.0 / 200.0},
                 {make_pair(-1, 1), 26.0 / 200.0},
                 {make_pair(1, 1), 30.0 / 200.0},
                 {make_pair(3, 1), 30.0 / 200.0},
                 {make_pair(-2, 2), 12.0 / 200.0},
                 {make_pair(0, 2), 26.0 / 200.0},
                 {make_pair(2, 2), 12.0 / 200.0},
                 {make_pair(-3, 3), 5.0 / 200.0},
                 {make_pair(-1, 3), 12.0 / 200.0},
                 {make_pair(1, 3), 12.0 / 200.0},
                 {make_pair(3, 3), 5.0 / 200.0}};
        break;
    }

    return d_map;
}

int VoxDithering::RequestData(vtkInformation *vtkNotUsed(request),
                              vtkInformationVector **inputVector, vtkInformationVector *outputVector)
{
    vtkInformation *inInfo = inputVector[0]->GetInformationObject(0);
    vtkImageData *inImg = vtkImageData::GetData(inInfo);

    vtkInformation *outInfo = outputVector->GetInformationObject(0);
    vtkImageData *outImg = vtkImageData::GetData(outInfo);
    outImg->DeepCopy(inImg);

    int *ext = outImg->GetExtent();

    for (int k = ext[4]; k < ext[5]; ++k)
    {
        for (int j = ext[2]; j < ext[3]; ++j)
        {
            for (int i = ext[0]; i < ext[1]; ++i)
            {
                double pixel = outImg->GetScalarComponentAsDouble(i, j, k, 0);
                double new_val = this->ClosestVal(pixel);

                double error = pixel - new_val;
                if (error != 0)
                {
                    outImg->SetScalarComponentFromDouble(i, j, k, 0, new_val);
                    DitherMap d_map = this->GetDitherMap(this->Dithering);

                    for (auto it = d_map.cbegin(); it != d_map.cend(); it++)
                    {
                        pair<int, int> id = it->first;
                        double error_diffusion = it->second;

                        int di = id.first + i;
                        int dj = id.second + j;

                        bool in_ext = ext[0] <= di && di <= ext[1] && ext[2] <= dj && dj <= ext[3];
                        if (in_ext)
                        {
                            double old_val = outImg->GetScalarComponentAsDouble(di, dj, k, 0);
                            double quantization = old_val - error * error_diffusion;
                            outImg->SetScalarComponentFromDouble(di, dj, k, 0, quantization);
                        }
                    }
                }
            }
        }
    }

    return 1;
}

void VoxDithering::PrintSelf(ostream &os, vtkIndent indent)
{
    this->Superclass::PrintSelf(os, indent);
}