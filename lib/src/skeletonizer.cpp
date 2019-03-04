#include "skeletonizer.h"
#include <CGAL/Arr_segment_traits_2.h>
#include <CGAL/Arrangement_2.h>
#include <CGAL/Arr_polyline_traits_2.h>
#include <CGAL/HalfedgeDS_decorator.h>

#include<CGAL/Polygon_with_holes_2.h>
#include<CGAL/create_offset_polygons_2.h>

#include <vtkPointData.h>
#include <vtkType.h>
#include <vtkIdList.h>
#include <vtkCellArray.h>
#include <vtkPolyLine.h>
#include <vtkPoints.h>

typedef CGAL::Arr_segment_traits_2<Kernel> segment_trait;
typedef CGAL::Arr_polyline_traits_2<segment_trait> Traits_2;

typedef Traits_2::Point_2 Point_2;
typedef Traits_2::Segment_2 Segment_2;
typedef Traits_2::Curve_2 Polyline_2;
typedef CGAL::Arrangement_2<Traits_2> Arrangement_2;

typedef CGAL::Polygon_2<Kernel> Polygon_2;
typedef CGAL::Polygon_with_holes_2<Kernel> Polygon_with_holes;

typedef boost::shared_ptr<Polygon_2> PolygonPtr;
typedef std::vector<PolygonPtr> PolygonPtrVector;

skeletonizer::skeletonizer(vtkPolyData* data)
{
    Traits_2 traits;
    Arrangement_2 arr(&traits);
    Traits_2::Construct_curve_2 polyline_construct = traits.construct_curve_2_object();

    vtkSmartPointer<vtkCellArray> cell_array = data->GetLines();
    cell_array->InitTraversal();

    vtkSmartPointer<vtkIdList> id_list = vtkSmartPointer<vtkIdList>::New();
    
    while(cell_array->GetNextCell(id_list))
    {
        vector<Point_2> points;
        int number_id = id_list->GetNumberOfIds();
        for(int i; i<number_id;i++)
        {
            int vertex_id = id_list->GetId(i);
            double* vertex = data->GetPoint(vertex_id);
            points.push_back(Point_2(vertex[0],vertex[1]));
        }

        Polyline_2 p = polyline_construct(points.begin(),points.end());
        insert(arr,p);
    }
    Arrangement_2::Face_iterator fit;

    for(fit = arr.faces_begin(); fit != arr.faces_end(); ++fit)
    {
        if(!fit->is_unbounded())
        {
            Arrangement_2::Ccb_halfedge_circulator ccw;
            Polygon_2 outer ;
            ccw = fit->outer_ccb();
            do
            {
                outer.push_back(ccw->source()->point());
            }while(++ccw != fit->outer_ccb());

            Polygon_with_holes poly_h(outer);
            
            Arrangement_2::Hole_iterator hit;
            for(hit = fit->holes_begin(); hit != fit->holes_end(); ++hit)
            {
                Polygon_2 inner ;
                Arrangement_2::Ccb_halfedge_circulator cw = *hit;
                do{
                    inner.push_back(cw->source()->point());
                }while(++cw != *hit);
                poly_h.add_hole(inner);
            }

            SsPtr str_sk = CGAL::create_interior_straight_skeleton_2(poly_h);
            this->straight_skeletons.push_back(str_sk);
        }
    }
};

vtkPolyData* skeletonizer::get_offset(double dist)
{
    vtkSmartPointer<vtkPolyData> offsets = vtkSmartPointer<vtkPolyData>::New();
    vtkSmartPointer<vtkPoints> points = vtkSmartPointer<vtkPoints>::New();
    vtkSmartPointer<vtkCellArray> line_array = vtkSmartPointer<vtkCellArray>::New();

    vector<SsPtr>::iterator it;
    for(it = this->straight_skeletons.begin(); it != this->straight_skeletons.end(); it++)
    {
        SsPtr str_sk = *it;
        PolygonPtrVector offset_polygons = CGAL::create_offset_polygons_2<Polygon_2>(dist,*str_sk);
        PolygonPtrVector::iterator it_polygon;
        for(it_polygon = offset_polygons.begin(); it_polygon != offset_polygons.end(); it_polygon++)
        {
            PolygonPtr poly_ptr = *it_polygon;
            poly_ptr->vertices_begin();
            Polygon_2::Vertex_iterator v_it;
            vtkSmartPointer<vtkPolyLine> poly_line = vtkSmartPointer<vtkPolyLine>::New();
            for(v_it = poly_ptr->vertices_begin(); v_it != poly_ptr->vertices_end(); v_it++)
            {
                Point_2 cgal_pt = *v_it;
                vtkIdType id = points->InsertNextPoint(cgal_pt.x().to_double(),cgal_pt.y().to_double(),0.0);
                poly_line->GetPointIds()->InsertNextId (id);
            }
            line_array->InsertNextCell(poly_line);
        }

    }

    offsets->SetPoints(points);
    offsets->SetLines(line_array);

    return offsets.GetPointer();
};