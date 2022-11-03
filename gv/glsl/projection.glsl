#line 2

// Keep these values in sync with projection.py
const int PERSPECTIVE_PROJECTION = 0;
const int ORTHOGRAPHIC_PROJECTION = 1;
const int AZIMUTHAL_EQUAL_AREA = 2;
const int EQUIRECTANGULAR_PROJECTION = 3;
const int AZIMUTHAL_EQUIDISTANT = 4;
const int STEREOGRAPHIC_PROJECTION = 5;
const int GNOMONIC_PROJECTION = 6;

const float pi = 3.14159265359;
const float two_pi = 2.0 * pi;

layout(std140, binding = 2) uniform TransformBlock
{
    int projection;  // 0 TODO: use a uniform block like this...
    int instanceID;  // 4 for (future) tiling equirectangular projection
    float view_height_radians;
    // there is room for 1 more scalar here...

    // linear transforms: display toward data
    mat4 ndc_X_nmc4;  // 16
    mat4 obq_X_ecf4;  // 80

    // linear transforms: data toward display
    mat4 ecf_X_obq4;  // 144
    mat4 nmc_X_ndc4;  // 208
    mat4 win_X_ndc4;  // 272
    // 336
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
    else if (ub.projection == PERSPECTIVE_PROJECTION) {
        float minx = 1 / (ub.view_height_radians + 1);
        if (obq.p1.x < minx && obq.p2.x < minx)
            return 0;  // Segment lies on the far side of the earth
    }
    result = obq;
    return 1;  // number of output segments
}

bool cull_obq(in vec3 obq)
{
    bool result = false;
    if (ub.projection == AZIMUTHAL_EQUAL_AREA) {
        result = obq.x < -0.99;
    }
    else if (ub.projection == AZIMUTHAL_EQUIDISTANT) {
        result = obq.x < -0.99;
    }
    else if (ub.projection == GNOMONIC_PROJECTION) {
        result = obq.x <= 0;
    }
    else if (ub.projection == ORTHOGRAPHIC_PROJECTION) {
        result = obq.x < 0;
    }
    else if (ub.projection == PERSPECTIVE_PROJECTION) {
        float minx = 1 / (ub.view_height_radians + 1);
        result = obq.x < minx;  // TODO: depend on view distance
    }
    else if (ub.projection == STEREOGRAPHIC_PROJECTION) {
        // avoid very long segments because they might cross the center.
        // especially the graticule at the south pole.
        // -0.98 is too low, clips some at min zoom
        result = obq.x < -0.999;
    }
    return result;
}

// Convert oblique geocentric directions to normalized map coordinates
vec2 dnmc_for_dobq(in vec3 dobq, in vec3 obq)
{
    // TODO: actually verify empirically these are correct
    // TODO: more projections
    if (ub.projection == AZIMUTHAL_EQUAL_AREA)
    {
        float s = sqrt(2 / (1 + obq.x));
        float d = 2 * (1 + obq.x);
        return vec2(
            dot(vec3(-s * obq.y / d, s, 0), dobq),
            dot(vec3(-s * obq.z / d, 0, s), dobq));
    }
    else if (ub.projection == AZIMUTHAL_EQUIDISTANT)
    {
        float ox = 1 - obq.x * obq.x;
        float ac = acos(obq.x);
        float xac = obq.x * ac;
        float d = xac / pow(ox, 1.5);
        float acs = ac / sqrt(ox);
        return vec2(
            dot(vec3(obq.y * d - obq.y / ox, acs, 0), dobq),
            dot(vec3(obq.z * d - obq.z / ox, 0, acs), dobq));
    }
    else if (ub.projection == EQUIRECTANGULAR_PROJECTION)
    {
        float d = obq.x * obq.x + obq.y * obq.y;
        return vec2(
            dot(vec3(-obq.y / d, obq.x / d, 0), dobq),
            dot(vec3(0, 0, 1 / sqrt(d)), dobq));
    }
    else if (ub.projection == GNOMONIC_PROJECTION)
    {
        float x2 = obq.x * obq.x;
        return vec2(
            dot(vec3(-obq.y / x2, 1 / obq.x, 0), dobq),
            dot(vec3(-obq.z / x2, 0, 1 / obq.x), dobq));
    }
    else if (ub.projection == ORTHOGRAPHIC_PROJECTION)
    {
        return vec2(
            dot(vec3(-obq.y / obq.x, 1, 0), dobq),
            dot(vec3(-obq.z / obq.x, 0, 1), dobq));
    }
    else if (ub.projection == PERSPECTIVE_PROJECTION)
    {
        float v = ub.view_height_radians;
        float d = 2 * (v + 1 - obq.x);
        return vec2(
            dot(vec3(v * obq.y / (d*d), v/d, 0), dobq),
            dot(vec3(v * obq.z / (d*d), 0, v/d), dobq));
    }
    else if (ub.projection == STEREOGRAPHIC_PROJECTION)
    {
        float xp = obq.x + 1;
        float d = 2 / xp;
        return vec2(
            dot(vec3(-obq.y * d / xp, d, 0), dobq),
            dot(vec3(-obq.z * d / xp, 0, d), dobq));
    }

    return vec2(0);  // whatever...
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
    switch(ub.projection) {
    case EQUIRECTANGULAR_PROJECTION:
        return vec3(atan(obq.y, obq.x), asin(obq.z), 1);
    case AZIMUTHAL_EQUAL_AREA:
    {
        float d = sqrt(2 / (1 + obq.x));
        return vec3(d * obq.y, d * obq.z, 1);
    }
    case AZIMUTHAL_EQUIDISTANT:
    {
        float d = acos(obq.x) / sqrt(1.0 - obq.x * obq.x);
        return vec3(d * obq.y, d * obq.z, 1);
    }
    case ORTHOGRAPHIC_PROJECTION:
        if (obq.x < 0) {
            // pull points past horizon back to horizon
            float s = 1.0 / length(obq.yz);
            return vec3(s * obq.y, s * obq.z, 1);
        }
        return vec3(obq.y, obq.z, 1);
    case PERSPECTIVE_PROJECTION:
    {
        float v = ub.view_height_radians;
        float max_radius = sqrt(v / (2 + v));  // nmc boundary
        float min_x = max_radius / v;
        float d = v / (v - obq.x + 1.0);
        vec2 nmc = obq.yz * d;
        if (obq.x < min_x) {
            // pull points past horizon back to horizon
            float s = max_radius / length(nmc);
            return vec3(s * nmc, 1);
        }
        return vec3(nmc, 1);
    }
    case STEREOGRAPHIC_PROJECTION: {
        float d = 1 + obq.x;
        if (d <= 0)
            return vec3(0, 0, 1);
        else
            return vec3(2 * obq.y / d, 2 * obq.z / d, 1);
    }
    case GNOMONIC_PROJECTION:
        return vec3(obq.y / obq.x, obq.z / obq.x, 1);
    default:
        return vec3(0);  // whatever...
    }
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
    else if (ub.projection == AZIMUTHAL_EQUAL_AREA)
    {
        float d1 = dot(prj, prj) / 2;
        float d2 = sqrt(1 - d1 / 2);
        return vec3(
            1 - d1,
            prj.x * d2,
            prj.y * d2);
    }
    else if (ub.projection == AZIMUTHAL_EQUIDISTANT)
    {
        float d = length(prj);
        float sdd = sin(d) / d;
        return vec3(
            cos(d),
            prj.x * sdd,
            prj.y * sdd);
    }
    else if (ub.projection == ORTHOGRAPHIC_PROJECTION)
        return vec3(
            sqrt(1.0 - dot(prj.xy, prj.xy)),
            prj.x,
            prj.y);
    else if (ub.projection == PERSPECTIVE_PROJECTION)
    {
        float v = ub.view_height_radians;
        float r2 = dot(prj.xy, prj.xy);
        float ox = (v * sqrt(v*v - v * (v + 2) * r2) + v * r2 + r2) / (v*v + r2);
        return vec3(
            ox,
            prj.x * (v + 1 - ox) / v,
            prj.y * (v + 1 - ox) / v);
    }
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

// combined functions below

vec3 ndc_for_nmc(in vec3 pos_nmc)
{
    vec3 ndc = mat3(ub.ndc_X_nmc4) * pos_nmc;
    return ndc.xyz;
}

vec3 ndc_for_obq(in vec3 pos_obq)
{
    return ndc_for_nmc(nmc_for_obq(pos_obq));
}

vec3 ecf_for_obq(in vec3 ecf)
{
    return mat3(ub.ecf_X_obq4) * ecf;
}

vec3 obq_for_ecf(in vec3 ecf)
{
    return mat3(ub.obq_X_ecf4) * ecf;
}

vec2 nmc_for_ecf(in vec3 ecf)
{
    return nmc_for_obq(obq_for_ecf(ecf)).xy;
}

vec3 ndc_for_ecf(in vec3 pos_ecf)
{
    return ndc_for_obq(obq_for_ecf(pos_ecf));
}

vec3 win_for_ndc(in vec3 ndc)
{
    return mat3(ub.win_X_ndc4) * ndc;
}

vec3 win_for_obq(in vec3 obq)
{
    return win_for_ndc(ndc_for_obq(obq));
}

vec3 win_for_ecf(in vec3 ecf)
{
    return win_for_ndc(ndc_for_ecf(ecf));
}

vec2 dwin_for_dobq(in vec3 dobq, in vec3 obq)
{
    vec2 dnmc = dnmc_for_dobq(dobq, obq);
    vec2 dndc = mat2(ub.ndc_X_nmc4) * dnmc;
    vec2 dwin = mat2(ub.win_X_ndc4) * dndc;
    return dwin;
}

vec2 dwin_for_decf(in vec3 decf, in vec3 ecf)
{
    vec3 obq = ecf_for_obq(ecf);
    vec3 dobq = obq_for_ecf(decf);
    return dwin_for_dobq(dobq, obq);
}
