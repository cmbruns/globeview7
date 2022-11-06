#ifndef CUSTOM_PROCESS_INCLUDES
#extension GL_GOOGLE_include_directive : enable
#include "waypoint.glsl"
#include "projection.glsl"
#endif

layout (vertices = 2) out;

in Waypoint3 tc_waypoint_obq[];
in vec4 fColor[];

out Waypoint3 te_waypoint_obq[];
patch out vec4 teColor;
patch out Waypoint3 midPoint;
patch out float midT;


float sine2DAngle(vec2 v1, vec2 v2)
{
    return abs(cross(vec3(v1, 0), vec3(v2, 0)).z);
}


void clipWaypoint(inout Waypoint3 wp_obq, bool useInDirection) {
    // hard code orthographic case for now
    // TODO: move to projection.glsl

    // TODO: this is orthographic specific
    if (wp_obq.p.x > 0) return;  // no clipping needed

    vec3 dir;
    if (useInDirection)
        dir = wp_obq.inDir;
    else
        dir = wp_obq.outDir;
    clip_obq_point(wp_obq.p);

    vec3 horizonSlope = vec3(0, wp_obq.p.z, -wp_obq.p.y);  // clockwise around horizon
    if (dot(dir, horizonSlope) < 0)
        horizonSlope = -horizonSlope;
    wp_obq.inDir = horizonSlope;
    wp_obq.outDir = horizonSlope;
}


float segmentTessLevel(in Waypoint3 wp0, in Waypoint3 wp1)
{
    // dynamically determine tessellation level
    vec3 obq0 = wp0.p;
    vec3 obq1 = wp1.p;
    vec3 win0 = win_for_obq(obq0);
    vec3 win1 = win_for_obq(obq1);
    vec2 dw = (win1 - win0).xy;
    float lw = length(dw);
    if (lw == 0)
        return 1;
    float nsegs = 1;  // minimum number of interpolated segments
    nsegs += lw / 100;  // more segments for longer lines
    if (lw > 0) {
        vec2 lineDir = dw / lw;
        vec2 dwin0 = dwin_for_dobq(wp0.outDir, obq0);
        vec2 dwin1 = dwin_for_dobq(wp1.inDir, obq1);
        if (length(dwin0) > 0 && length(dwin1) > 0) {
            vec2 m0 = normalize(dwin0);
            vec2 m1 = normalize(dwin1);
            float c0 = 1 - dot(m0, lineDir);// 1 minus cosine of slope angle wrt line
            float c1 = 1 - dot(m1, lineDir);
            float cmax = max(c0, c1);// range 0 to 2
            nsegs += 100 * cmax;  // more segments for more dramatic curves
        }
        vec2 dnmc0 = dnmc_for_dobq(wp0.outDir, obq0);
        vec2 dnmc1 = dnmc_for_dobq(wp1.inDir, obq1);
        if (false && isnan(length(dwin0)) || isnan(length(dwin1))) {
            teColor = vec4(1, 0.5, 0.5, 1);  // pink for debugging
        }
    }
    return nsegs;
}


void main()
{
    teColor = fColor[0];

    Waypoint3 wp0 = tc_waypoint_obq[0];
    Waypoint3 wp1 = tc_waypoint_obq[1];
    clipWaypoint(wp0, true);
    clipWaypoint(wp1, false);
    bool down0 = tc_waypoint_obq[0].p.x < 0;
    bool down1 = tc_waypoint_obq[1].p.x < 0;

    if (gl_InvocationID == 0)  // begin point of input segment
    {
        // dynamically determine tessellation level
        gl_TessLevelOuter[0] = 1.0;  // Number of lines
        gl_TessLevelOuter[1] = segmentTessLevel(wp0, wp1);  // Number of segments per line
        gl_TessLevelOuter[2] = 1.0;  // Unused, but needed for validation
        gl_TessLevelOuter[3] = 1.0;  // Unused, but needed for validation

        te_waypoint_obq[gl_InvocationID] = wp0;

        if (false) {
            // Color by horizon relationship for testing and debugging
            teColor = vec4(0, 1, 0, 1);  // green for segment above horizon
            if (down0 && down1)
                teColor = vec4(1, 0, 0, 1);  // red for segment below horizon
            else if (down0 || down1)
                teColor = vec4(1, 1, 0, 1);  // yellow for segment crossing horizon
        }

        // TODO: handle horizon crossing segments
        // TODO: for segments that cross the horizon in orthographic,
        //   put a sharp corner at the horizon boundary
        // TODO: this is orthographic specific
        if (!down0 && !down1) {
            // Both segment endpoints are above the horizon
            // Simply interpolate in the main play area
            // TODO: what if some part in the middle goes below the horizon?
            midT = 0.5;
            midPoint = interpolateWaypoint(
                tc_waypoint_obq[0], tc_waypoint_obq[1], midT);
        }
        else if (down0 && down1) {
            // Segment is entirely below the horizon
            // Simply interpolate along the horizon
            // TODO: what if some part in the middle goes above the horizon?
            midT = 0.5;
            midPoint = interpolateWaypoint(wp0, wp1, midT);
        }
        else {
            // Segment definitely crosses the horizon.
            // Create a sharp corner at the horizon.
            // TODO: solve exact horizon crossing using cubic formula
            // for now use linear approximation to find t where x==0
            float horizonT = tc_waypoint_obq[0].p.x / (tc_waypoint_obq[0].p.x - tc_waypoint_obq[1].p.x);
            // teColor = vec4(horizonT, 1 - horizonT, horizonT, 1);
            Waypoint3 horizonWp = interpolateWaypoint(tc_waypoint_obq[0], tc_waypoint_obq[1], horizonT);
            horizonWp.p = vec3(0, normalize(horizonWp.p.yz));  // Clamp to exact x==0
            vec3 horizonSlope = vec3(0, horizonWp.p.z, -horizonWp.p.y);  // clockwise around horizon
            if (down0) {
                // first endpoint is below the horizon, so set the INPUT direction to the horizon direction
                if (dot(horizonWp.inDir, horizonSlope) < 0)
                    horizonSlope = -horizonSlope;
                horizonWp.inDir = horizonSlope;
            }
            else {
                // second endpoint is below the horizon, so set the OUTPUT direction to the horizon direction
                if (dot(horizonWp.outDir, horizonSlope) < 0)
                    horizonSlope = -horizonSlope;
                horizonWp.outDir = horizonSlope;
                float tess0 = segmentTessLevel(wp0, horizonWp);
                float tess1 = segmentTessLevel(horizonWp, wp1);
                midT = tess0 / (tess0 + tess1);
                // teColor = vec4(midT, 1, 0, 1);
            }
            midPoint = horizonWp;
            // The two subsegments might have different tesselation requirements
            float tess0 = segmentTessLevel(wp0, horizonWp);
            float tess1 = segmentTessLevel(horizonWp, wp1);
            midT = tess0 / (tess0 + tess1);
        }
    }
    else if (gl_InvocationID == 1)  // end point of input segment
    {
        te_waypoint_obq[gl_InvocationID] = wp1;
    }
}
