#pragma include "waypoint.glsl"
#pragma include "projection.glsl"

layout (vertices = 2) out;

in Waypoint3 tc_waypoint_obq[];
in vec4 fColor[];

uniform bool uContainsAntipode = false;

out Waypoint3 te_waypoint_obq[];
out vec4 teColor[];


float sine2DAngle(vec2 v1, vec2 v2)
{
    return abs(cross(vec3(v1, 0), vec3(v2, 0)).z);
}


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


void main()
{
    // Color by horizon for testing and debugging
    vec4 testColor = vec4(0, 1, 0, 1);  // green for segment above horizon
    bool down0 = tc_waypoint_obq[0].p.x < 0;
    bool down1 = tc_waypoint_obq[1].p.x < 0;
    if (down0 && down1)
        testColor = vec4(1, 0, 0, 1);  // red for segment below horizon
    else if (down0 || down1)
        testColor = vec4(1, 1, 0, 1);  // yellow for segment crossing horizon


    if (gl_InvocationID == 0)
    {
        gl_TessLevelOuter[0] = 1.0;  // Number of lines
        gl_TessLevelOuter[1] = 1.0;  // Number of segments per line
        gl_TessLevelOuter[2] = 1.0;  // Unused, but needed for validation
        gl_TessLevelOuter[3] = 1.0;  // Unused, but needed for validation

        // dynamically determine tessellation level
        Waypoint3 wp0 = tc_waypoint_obq[0];
        Waypoint3 wp1 = tc_waypoint_obq[1];
        clipWaypoint(wp0, uContainsAntipode);
        clipWaypoint(wp1, uContainsAntipode);
        vec3 obq0 = wp0.p;
        vec3 obq1 = wp1.p;
        vec3 win0 = win_for_obq(obq0);
        vec3 win1 = win_for_obq(obq1);
        vec2 dw = (win1 - win0).xy;
        float lw = length(dw);
        float nsegs = 1;  // minimum number of interpolated segments
        nsegs += lw / 100;  // more segments for longer lines
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

        gl_TessLevelOuter[1] = nsegs;  // Number of segments per line
    }

    Waypoint3 wp = tc_waypoint_obq[gl_InvocationID];
    clipWaypoint(wp, uContainsAntipode);
    te_waypoint_obq[gl_InvocationID] = wp;
    gl_out[gl_InvocationID].gl_Position = vec4(wp.p, 1);  // not needed?
    teColor[gl_InvocationID] = testColor; // fColor[gl_InvocationID];
}
