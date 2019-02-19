#ifndef SKELETONIZER_H
#define SKELETONIZER_H

#include <vtkPolyData.h>
#include <vector>
#include <vtkSmartPointer.h>
#include <CGAL/Cartesian.h>
#include <CGAL/Exact_rational.h>
#include <CGAL/create_straight_skeleton_from_polygon_with_holes_2.h>
#include <boost/shared_ptr.hpp>

typedef CGAL::Cartesian<CGAL::Exact_rational> Kernel;
typedef CGAL::Straight_skeleton_2<Kernel>  Ss;
typedef boost::shared_ptr<Ss> SsPtr;

using namespace std;

class skeletonizer
{
    public:
        skeletonizer(vtkPolyData* data);
        vtkSmartPointer<vtkPolyData> get_offset(double dist);
    private:
        vector<SsPtr> straight_skeletons;
};

#endif