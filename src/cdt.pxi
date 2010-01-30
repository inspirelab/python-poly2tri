cdef class CDT:

    cdef c_CDT *me
    cdef point_vec polyline
    
    def __init__(self, list polyline):
        self.polyline = pointvec_factory(0)
        for point in polyline:
            self.polyline.push_back(new_Point(point.x, point.y))
        self.me = new_CDT(self.polyline)
    
    def triangulate(self):
        self.me.Triangulate()
                
    property triangles:
        def __get__(self): 
          cdef triangle_vec tri_list = self.me.GetTriangles()
          tris = []
          for i in range(tri_list.size()):
              a = Point(tri_list.get(i).GetPoint(0).x, tri_list.get(i).GetPoint(0).y)
              b = Point(tri_list.get(i).GetPoint(1).x, tri_list.get(i).GetPoint(1).y)
              c = Point(tri_list.get(i).GetPoint(2).x, tri_list.get(i).GetPoint(2).y)
              tris.append(Triangle(a, b, c))
          return tris

    def __dealloc__(self):
        pass
        #del_CDT(self.me)