#pragma include "waypoint.glsl"
#pragma include "projection.glsl"

layout (vertices = 2) out;

in Waypoint3 tc_waypoint_obq[];
in vec4 fColor[];

out Waypoint3 te_waypoint_obq[];
out vec4 teColor[];


float sine2DAngle(vec2 v1, vec2 v2)
{
    return abs(cross(vec3(v1, 0), vec3(v2, 0)).z);
}


void main()
{
    if (gl_InvocationID == 0)
    {
        gl_TessLevelOuter[0] = 1.0;  // Number of lines
        gl_TessLevelOuter[1] = 1.0;  // Number of segments per line
        gl_TessLevelOuter[2] = 1.0;  // Unused, but needed for validation
        gl_TessLevelOuter[3] = 1.0;  // Unused, but needed for validation

        // dynamically determine tessellation level
        Waypoint3 wp0 = tc_waypoint_obq[0];
        Waypoint3 wp1 = tc_waypoint_obq[1];
        vec3 obq0 = wp0.p;
        vec3 obq1 = wp1.p;
        vec3 win0 = win_for_obq(obq0);
        vec3 win1 = win_for_obq(obq1);
        vec2 dw = (win1 - win0).xy;
        float lw = length(dw);
        float nsegs = 1;  // minimum number of interpolated segments
        nsegs += lw / 15;  // more segments for longer lines
        if (lw > 0) {
            vec2 lineDir = dw / lw;
            vec2 m0 = normalize(dwin_for_dobq(wp0.outDir, obq0));
            vec2 m1 = normalize(dwin_for_dobq(wp1.inDir, obq1));
            float c0 = 1 - dot(m0, lineDir);  // 1 minus cosine of slope angle wrt line
            float c1 = 1 - dot(m1, lineDir);
            float cmax = max(c0, c1);  // range 0 to 2
            nsegs += 100 * cmax;  // more segments for more dramatic curves
        }

        gl_TessLevelOuter[1] = nsegs;  // Number of segments per line
    }

    gl_out[gl_InvocationID].gl_Position = gl_in[gl_InvocationID].gl_Position;  // not needed?
    te_waypoint_obq[gl_InvocationID] = tc_waypoint_obq[gl_InvocationID];
    teColor[gl_InvocationID] = fColor[gl_InvocationID];
}
