#line 2

// Keep these values in sync with projection.py
const int EQUIRECTANGULAR_PROJECTION = 0;
const int ORTHOGRAPHIC_PROJECTION = 1;
const float pi = 3.14159265359;
const float two_pi = 2.0 * pi;

layout(std140) uniform TransformBlock
{
    int projection;  // TODO: use a uniform block like this...
} ub;

struct Segment2
{
    vec2 p1;
    vec2 p2;
};

struct Segment3
{
    vec3 p1;
    vec3 p2;
};

int clip_nmc_segment(in Segment3 nmc, in int projection, out Segment3[2] result)
{
    if (projection == EQUIRECTANGULAR_PROJECTION) {
        if (abs(nmc.p1.x - nmc.p2.x) > pi/2) {
            // segment crosses seam
            // Enforce left to right for simpler clipping
            vec3 left = nmc.p1;
            vec3 right = nmc.p2;
            if (left.x > right.x) {
                left = nmc.p2;
                right = nmc.p1;
            }
            float alpha = (left.x + pi) / (left.x + pi + pi - right.x);
            vec3 mid = vec3(-pi, mix(left.yz, right.yz, alpha));
            result[0] = Segment3(left, mid);
            mid.x = pi;
            result[1] = Segment3(mid, right);
            return 2;
        }
    }
    result[0] = nmc;
    return 1;  // number of output segments
}

int clip_obq_segment(in Segment3 obq, in int projection, out Segment3 result)
{
    if (projection == ORTHOGRAPHIC_PROJECTION) {
        if (obq.p1.x < 0 && obq.p2.x < 0)
            return 0;  // Segment lies on the far side of the earth
        // TODO: compute clipped segment
    }
    result = obq;
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
