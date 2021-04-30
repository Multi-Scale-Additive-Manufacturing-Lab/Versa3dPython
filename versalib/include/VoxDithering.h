/*
 * File: VoxDithering.h
 * Project: Versa3d
 * File Created: 2021-04-30
 * Author: Marc Wang (marc.wang@uwaterloo.ca)
 * -----
 * Last Modified: 2021-04-30
 * Modified By: Marc Wang (marc.wang@uwaterloo.ca>)
 * -----
 * Copyright (c) 2021, MSAM Lab - University of Waterloo
 */

#ifndef VOXDITHERING_H
#define VOXDITHERING_H
#include <map>
#include "vtkImageAlgorithm.h"

using namespace std;

#define DitherMap map<pair<int, int>, float>

namespace
{
    class VoxDithering : public vtkImageAlgorithm
    {
    public:
        vtkTypeMacro(VoxDithering, vtkImageAlgorithm);
        void PrintSelf(ostream &os, vtkIndent indent) override;
        enum class DitheringType : int
        {
            floyd_steinberg,
            atkinson,
            jarvis_judice_ninke,
            stucki,
            burkes,
            sierra3,
            sierra2,
            sierra2_4a,
            stevenson_arce
        };

        //vtkSetMacro(Dithering, DitheringType);
        //vtkGetMacro(Dithering, DitheringType);
        DitherMap GetDitherMap(DitheringType type);

    protected:
        VoxDithering();
        ~VoxDithering() override = default;

        int RequestInformation(vtkInformation *, vtkInformationVector **, vtkInformationVector *) override;

        // see vtkAlgorithm for details
        int RequestData(vtkInformation *request, vtkInformationVector **inputVector,
                        vtkInformationVector *outputVector) override;

    private:
        void operator=(const VoxDithering &) = delete;
        double ClosestVal(double pixel);
        DitheringType Dithering;
    };

}

#endif