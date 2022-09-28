const int EQUIRECTANGULAR_PROJECTION = 0;
const int ORTHOGRAPHIC_PROJECTION = 1;

// Convert oblique geocentric coordinates to normalized map coordinates
vec3 nmc_for_obq(in vec3 obq, in int projection)
{
    if (projection == EQUIRECTANGULAR_PROJECTION)
        return vec3(atan(obq.y, obq.x), asin(obq.z), 1);
    else if (projection == ORTHOGRAPHIC_PROJECTION)
        return vec3(obq.y, obq.z, 1);
    else
        return vec3(0);  // whatever...
}

// Convert WGS84 coordinates to non-oblique geocentric coordinates
vec3 ecf_for_wgs(vec2 wgs /* lon, lat radians */)
{
    return vec3(
        cos(wgs.x) * cos(wgs.y),  // x thither
        sin(wgs.x) * cos(wgs.y),  // y right
        sin(wgs.y));  // z up
}
