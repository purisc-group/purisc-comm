typedef unsigned int uint;

typedef struct{
    uint  x, y, z, w; 
}uint4;

typedef struct{
    int x, y;
}int2;

typedef struct{
    uint x,y,z;
}uint3;

int get_global_id(int id);

