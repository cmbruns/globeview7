#line 2

// Keep these values in sync with projection.py
const int EQUIRECTANGULAR_PROJECTION = 0;
const int ORTHOGRAPHIC_PROJECTION = 1;
const int STEREOGRAPHIC_PROJECTION = 2;
const int GNOMONIC_PROJECTION = 3;

const float pi = 3.14159265359;
const float two_pi = 2.0 * pi;

layout(std140, binding = 2) uniform TransformBlock
{
    int projection;  // 0 TODO: use a uniform block like this...
    int instanceID;  // 4 for (future) tiling equirectangular projection
    // there is room for 2 more scalars here...

    // linear transforms: display toward data
    mat4 ndc_X_nmc4;  // 16
    mat4 obq_X_ecf4;  // 80

    // linear transforms: data toward display
    mat4 ecf_X_obq4;  // 144
    mat4 nmc_X_ndc4;  // 208
    // 272
} ub;

struct Segment3
{
    vec3 p1;
    vec3 p2;
};

int clip_nmc_segment(in Segment3 nmc, out Segment3[2] result)
{
    if (ub.projection == EQUIRECTANGULAR_PROJECTION) {
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
    else if (ub.projection == GNOMONIC_PROJECTION) {
        // avoid very long segments that might cause artifacts
        vec2 diff = nmc.p1.xy - nmc.p2.xy;
        float d2 = dot(diff, diff);
        if (d2 > 100)
            return 0;
    }
    result[0] = nmc;
    return 1;  // number of output segments
}

int clip_obq_segment(in Segment3 obq, out Segment3 result)
{
    if (ub.projection == ORTHOGRAPHIC_PROJECTION)
    {
        if (obq.p1.x < 0 && obq.p2.x < 0)
            return 0;  // Segment lies on the far side of the earth
        // TODO: compute clipped segment
    }
    else if (ub.projection == GNOMONIC_PROJECTION)
    {
        if (obq.p1.x <= 0 && obq.p2.x <= 0)
            return 0;  // Segment lies on the far side of the earth
        // TODO: compute clipped segment
    }
    result = obq;
    return 1;  // number of output segments
}

bool cull_obq(in vec3 obq)
{
    bool result = false;
    if (ub.projection == ORTHOGRAPHIC_PROJECTION) {
        result = obq.x < 0;
    }
    else if (ub.projection == STEREOGRAPHIC_PROJECTION) {
        // avoid very long segments because they might cross the center.
        // especially the graticule at the south pole.
        // -0.98 is too low, clips some at min zoom
        result = obq.x < -0.999;
    }
    else if (ub.projection == GNOMONIC_PROJECTION) {
        result = obq.x <= 0;
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
vec3 nmc_for_obq(in vec3 obq)
{
    if (ub.projection == EQUIRECTANGULAR_PROJECTION)
        return vec3(atan(obq.y, obq.x), asin(obq.z), 1);
    else if (ub.projection == ORTHOGRAPHIC_PROJECTION)
        return vec3(obq.y, obq.z, 1);
    else if (ub.projection == STEREOGRAPHIC_PROJECTION) {
        float d = 1 + obq.x;
        if (d <= 0)
            return vec3(0, 0, 1);
        else
            return vec3(2 * obq.y / d, 2 * obq.z / d, 1);
    }
    else if (ub.projection == GNOMONIC_PROJECTION)
        return vec3(obq.y / obq.x, obq.z / obq.x, 1);
    else
        return vec3(0);  // whatever...
}

// Convert normalized map coordinates to oblique geocentric coorinates
vec3 obq_for_nmc(in vec3 nmc)
{
    vec2 prj = nmc.xy / nmc.z;
    if (ub.projection == EQUIRECTANGULAR_PROJECTION)
        return vec3(
            cos(prj.x) * cos(prj.y),
            sin(prj.x) * cos(prj.y),
            sin(prj.y));
    else if (ub.projection == ORTHOGRAPHIC_PROJECTION)
        return vec3(
            sqrt(1.0 - dot(prj.xy, prj.xy)),
            prj.x,
            prj.y);
    else if (ub.projection == STEREOGRAPHIC_PROJECTION)
    {
        float d = 4.0 + prj.x * prj.x + prj.y * prj.y;
        return vec3(
            (8.0 - d) / d,
            4.0 * prj.x / d,
            4.0 * prj.y / d);
    }
    else if (ub.projection == GNOMONIC_PROJECTION)
    {
        float oy = 1.0 / sqrt(1.0 + prj.x * prj.x + prj.y * prj.y);
        return vec3(
            oy,
            prj.x * oy,
            prj.y * oy);
    }
    else
        return vec3(0);  // whatever...
}

vec2 wgs_for_ecf(in vec3 ecf)
{
    return vec2(atan(ecf.y, ecf.x), asin(ecf.z));
}
