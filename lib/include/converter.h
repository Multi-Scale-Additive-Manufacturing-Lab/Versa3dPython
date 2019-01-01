#include <pybind11/pybind11.h>

#define VTK_TYPE_CASTER(vtk_object, py_vtk) \
    namespace pybind11 { namespace detail { \
        template <> \
        struct type_caster<vtk_object> { \
        protected: \
            vtk_object* value; \
        public: \
            bool load(handle src, bool) { \
                char thisStr[] = "__this__"; \
                PyObject *source = src.ptr(); \
                if(!PyObject_HasAttrString(source, thisStr)) {return false;}\
                PyObject *thisAttr = PyObject_GetAttrString(source, thisStr); \
                if(thisAttr == NULL){return false;}\
                PyObject* pyStr = PyUnicode_AsEncodedString(thisAttr, "utf-8","Error ~");\
                char* str = PyBytes_AS_STRING(pyStr);\
                if(str == 0 || strlen(str) < 1){return false;} \
                char hex_address[32], *pEnd; \
                char *_p_ = strstr(str, "_p_vtk"); \
                if(_p_ == NULL) return NULL; \
                char *class_name = strstr(_p_, "vtk"); \
                if(class_name == NULL) return NULL; \
                strcpy(hex_address, str+1); \
                hex_address[_p_-str-1] = '\0'; \
                long address = strtol(hex_address, &pEnd, 16); \
                value = (vtk_object*)((void*)address);\
                if(value->IsA(class_name)){return true;} \
                return false; \
            }\
            static handle cast(vtk_object src, return_value_policy, handle) {\
                if(&src == NULL){return Py_INCREF(Py_None)} \
                std::ostringstream oss; \
                oss << (vtkObjectBase*) &src; \
                std::string address_str = oss.str(); \
                object obj = import("vtk").attr("vtkObjectBase")(address_str); \
                return Py_INCREF(obj.ptr()); \
            } \
        }; \
    }}
