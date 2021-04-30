/*
 * File: VersaLib_wrapper.cc
 * Project: Versa3d
 * File Created: 2021-04-30
 * Author: Marc Wang (marc.wang@uwaterloo.ca)
 * -----
 * Last Modified: 2021-04-30
 * Modified By: Marc Wang (marc.wang@uwaterloo.ca>)
 * -----
 * Copyright (c) 2021, MSAM Lab - University of Waterloo
 */

#include <pybind11/pybind11.h>

namespace py = pybind11;

PYBIND11_MODULE(OasisLib, m)
{
    m.doc() = "VersaLib";
}