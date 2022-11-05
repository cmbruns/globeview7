#ifndef CUSTOM_PROCESS_INCLUDES
#extension GL_GOOGLE_include_directive : enable
#include "waypoint.glsl"
#include "projection.glsl"
#endif

layout (vertices = 3) out;

in Waypoint3 tc_waypoint_obq[];
in vec4 fColor[];

uniform bool uContainsAntipode = false;

out Waypoint3 te_waypoint_obq[];
patch out vec4 teColor;
patch out float midT;


float sine2DAngle(vec2 v1, vec2 v2)
{
    return abs(cross(vec3(v1, 0), vec3(v2, 0)).z);
}


// TODO: antipode might not be the right way to choose the horizon direction.
// maybe better to follow the trend of either the horizon point, or the
// past horizon point.
void clipWaypoint(inout Waypoint3 wp_obq, in bool bContainsAntipode) {
    // hard code orthographic case for now
    // TODO: move to projection.glsl

    // TODO: this is orthographic specific
    if (wp_obq.p.x > 0) return;  // no clipping needed
    clip_obq_point(wp_obq.p);
    wp_obq.outDir = vec3(0, wp_obq.p.z, -wp_obq.p.y);  // clockwise around horizon
    if (bContainsAntipode)
        wp_obq.outDir = -wp_obq.outDir;  // counterclockwise
    wp_obq.inDir = wp_obq.outDir;  // clockwise around horizon
}


float segmentTessLevel(in Waypoint3 wp0, in Waypoint3 wp1)
{
    return 11;
    // dynamically determine tessellation level
    vec3 obq0 = wp0.p;
    vec3 obq1 = wp1.p;
    vec3 win0 = win_for_obq(obq0);
    vec3 win1 = win_for_obq(obq1);
    vec2 dw = (win1 - win0).xy;
    float lw = length(dw);
    float nsegs = 1;  // minimum number of interpolated segments
    // nsegs += lw / 20;  // more segments for longer lines
    if (lw > 0) {
        vec2 lineDir = dw / lw;
        vec2 m0 = normalize(dwin_for_dobq(wp0.outDir, obq0));
        vec2 m1 = normalize(dwin_for_dobq(wp1.inDir, obq1));
        float c0 = 1 - dot(m0, lineDir);  // 1 minus cosine of slope angle wrt line
        float c1 = 1 - dot(m1, lineDir);
        float cmax = max(c0, c1);  // range 0 to 2
        // TODO: no red lines when I uncomment line below...
        // nsegs += 10 * cmax;  // more segments for more dramatic curves
    }
    return nsegs;
}


void main()
{
    Waypoint3 wp0 = tc_waypoint_obq[0];
    Waypoint3 wp1 = tc_waypoint_obq[1];
    clipWaypoint(wp0, uContainsAntipode);
    clipWaypoint(wp1, uContainsAntipode);
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

        // Color by horizon relationship for testing and debugging
        teColor = vec4(0, 1, 0, 1);  // green for segment above horizon
        if (down0 && down1)
            teColor = vec4(1, 0, 0, 1);  // red for segment below horizon
        else if (down0 || down1)
            teColor = vec4(1, 1, 0, 1);  // yellow for segment crossing horizon
    }
    else if (gl_InvocationID == 1)  // mid point of input segment
    {
        // TODO: handle horizon crossing segments
        // TODO: for segments that cross the horizon in orthographic,
        //   put a sharp corner at the horizon boundary
        // TODO: this is orthographic specific
        if (!down0 && !down1) {
            // Both segment endpoints are above the horizon
            // Simply interpolate in the main play area
            // TODO: what if some part in the middle goes below the horizon?
            midT = 0.5;
            te_waypoint_obq[gl_InvocationID] = interpolateWaypoint(
                tc_waypoint_obq[0], tc_waypoint_obq[1], midT);
        }
        else if (down0 && down1) {
            // Segment is entirely below the horizon
            // Simply interpolate along the horizon
            // TODO: what if some part in the middle goes above the horizon?
            midT = 0.5;
            te_waypoint_obq[gl_InvocationID] = interpolateWaypoint(wp0, wp1, midT);
        }
        else {
            // Segment definitely crosses the horizon.
            // Create a sharp corner at the horizon.
            // TODO: solve exact horizon crossing using cubic formula
            // for now use linear approximation
            // float horizonT =
            midT = 0.5;
            te_waypoint_obq[gl_InvocationID] = interpolateWaypoint(wp0, wp1, midT);
        }
    }
    else if (gl_InvocationID == 2)  // end point of input segment
    {
        te_waypoint_obq[gl_InvocationID] = wp1;
    }
}
