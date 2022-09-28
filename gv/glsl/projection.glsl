#line 2

// Keep these values in sync with projection.py
const int EQUIRECTANGULAR_PROJECTION = 0;
const int ORTHOGRAPHIC_PROJECTION = 1;

layout(std140) uniform TransformBlock
{
    int projection;  // TODO: use a uniform block like this...
} ub;

struct Segment
{
    vec3 p1;
    vec3 p2;
};

int clip_obq_segment(in Segment obq, in int projection, out Segment[2] result)
{
    result[0] = obq;
    return 1;  // number of output segments
}

bool cull_obq(in vec3 obq, in int projection)
{
    bool result = false;
    if (projection == ORTHOGRAPHIC_PROJECTION) {
        result = obq.x < 0;
    }
    return result;
}

// Convert WGS84 coordinates to non-oblique geocentric coordinates
vec3 ecf_for_wgs(vec2 wgs /* lon, lat radians */)
{
    return vec3(
        cos(wgs.x) * cos(wgs.y),  // x thither
        sin(wgs.x) * cos(wgs.y),  // y right
        sin(wgs.y));  // z up
}

vec2 mercator_for_lonlat(in vec2 lonlat)
{
    return vec2(lonlat.x, log(tan(radians(45) + lonlat.y/2.0)));
}

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

// Convert normalized map coordinates to oblique geocentric coorinates
vec3 obq_for_nmc(in vec3 nmc, in int projection)
{
    vec2 prj = nmc.xy / nmc.z;
    if (projection == EQUIRECTANGULAR_PROJECTION)
        return vec3(
            cos(prj.x) * cos(prj.y),
            sin(prj.x) * cos(prj.y),
            sin(prj.y));
    else if (projection == ORTHOGRAPHIC_PROJECTION)
        return vec3(
            sqrt(1.0 - dot(prj.xy, prj.xy)),
            prj.x,
            prj.y);
    else
        return vec3(0);  // whatever...
}

vec2 wgs_for_ecf(in vec3 ecf)
{
    return vec2(atan(ecf.y, ecf.x), asin(ecf.z));
}
