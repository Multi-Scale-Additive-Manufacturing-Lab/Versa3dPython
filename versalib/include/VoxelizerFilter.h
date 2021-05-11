/*
 * File: VoxelizerFilter.h
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

#ifndef VOXELIZERFILTER_H
#define VOXELIZERFILTER_H
#include <array>

#include "vtkImageAlgorithm.h"
#include "vtkInformation.h"
#include "vtkInformationVector.h"

class VoxelizerFilter : public vtkImageAlgorithm
{
public:
    vtkTypeMacro(VoxelizerFilter, vtkImageAlgorithm);
    void PrintSelf(ostream &os, vtkIndent indent) override;

    static VoxelizerFilter *New();
    vtkSetVector3Macro(Dpi, int);
    vtkGetVector3Macro(Dpi, int);

protected:
    VoxelizerFilter();
    ~VoxelizerFilter() override = default;

    // see vtkAlgorithm for details
    int RequestData(vtkInformation *request, vtkInformationVector **inputVector,
                    vtkInformationVector *outputVector) override;
    int RequestInformation(vtkInformation *request, vtkInformationVector **inputVector,
                           vtkInformationVector *outputVector) override;

    int FillInputPortInformation(int port, vtkInformation *info);

private:
    void operator=(const VoxelizerFilter &) = delete;
    int Dpi[3];
    double ForegroundValue;
    double BackgroundValue;
    int ScalarType;
    int SampleDimensions[3];
    double ModelBounds[6];
};

#endif