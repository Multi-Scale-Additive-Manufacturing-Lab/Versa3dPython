/*
 * File: VersaLib_wrapper.cc
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

#include <pybind11/pybind11.h>

#include "PybindVTKTypeCaster.h"
#include "VoxelizerFilter.h"
#include "vtkNew.h"
#include "vtkImageData.h"
#include "vtkAlgorithmOutput.h"
#include "vtkObjectBase.h"

namespace py = pybind11;
using rvp = py::return_value_policy;

struct VtkDeleter
{
    void operator()(vtkObjectBase *p)
    {
        p->Delete();
    }
};

PYBIND11_MODULE(_versalib, m)
{
    m.doc() = "VersaLib";

    py::class_<VoxelizerFilter, std::unique_ptr<VoxelizerFilter, VtkDeleter>>(m, "VoxelizerFilter")
        .def(py::init([]() {
            return VoxelizerFilter::New();
        }))
        .def("GetOutput", py::overload_cast<int>(&VoxelizerFilter::GetOutput), rvp::reference)
        .def("GetOutputPort", py::overload_cast<int>(&VoxelizerFilter::GetOutputPort), rvp::reference)
        .def("SetInputConnection", py::overload_cast<vtkAlgorithmOutput*>(&VoxelizerFilter::SetInputConnection))
        .def("Update", py::overload_cast<int>(&VoxelizerFilter::Update));
}