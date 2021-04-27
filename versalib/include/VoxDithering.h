#ifndef VOXDITHERING_H
#define VOXDITHERING_H

#include "vtkImageAlgorithm.h"

namespace
{
    class VoxDithering : public vtkImageAlgorithm
    {
    public:
        vtkTypeMacro(VoxDithering, vtkImageAlgorithm);
        void PrintSelf(ostream& os, vtkIndent indent) override;

    protected:
        VoxDithering();
        ~VoxDithering() override = default;

        int RequestInformation(vtkInformation *, vtkInformationVector **, vtkInformationVector *) override;

        // see vtkAlgorithm for details
        int RequestData(vtkInformation *request, vtkInformationVector **inputVector,
                        vtkInformationVector *outputVector) override;

        // see algorithm for more info
        int FillInputPortInformation(int port, vtkInformation *info) override;
    
    private:
        void operator=(const VoxDithering&) = delete;

    };

}

#endif