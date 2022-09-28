const int EQUIRECTANGULAR_PROJECTION = 0;
const int ORTHOGRAPHIC_PROJECTION = 1;

vec3 nmc_for_obq(in vec3 obq, in int projection)
{
    if (projection == EQUIRECTANGULAR_PROJECTION)
        return vec3(atan(obq.y, obq.x), asin(obq.z), 1);
    else if (projection == ORTHOGRAPHIC_PROJECTION)
        return vec3(obq.y, obq.z, 1);
    else
        return vec3(0);  // whatever...
}
