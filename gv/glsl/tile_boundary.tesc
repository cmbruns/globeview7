#line 2
#pragma include "waypoint.glsl"
#pragma include "projection.glsl"

layout (vertices = 2) out;

in vec3 tc_inDir[];
in vec3 tc_outDir[];
in Waypoint3 tc_waypoint_obq[];
in vec4 fColor[];

out vec3 te_inDir[];
out vec3 te_outDir[];
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
        vec3 obq0 = tc_waypoint_obq[0].p;
        vec3 obq1 = tc_waypoint_obq[1].p;
        vec3 win0 = win_for_obq(obq0);
        vec3 win1 = win_for_obq(obq1);
        vec2 dw = (win1 - win0).xy;
        float lw = length(dw);
        float nsegs = 1;  // minimum number of interpolated segments
        nsegs += lw / 15;  // more segments for longer lines
        if (lw > 0) {
            vec2 lineDir = dw / lw;
            vec2 m0 = normalize(dwin_for_dobq(tc_outDir[0], obq0));
            vec2 m1 = normalize(dwin_for_dobq(tc_inDir[1], obq1));
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

    te_inDir[gl_InvocationID] = tc_inDir[gl_InvocationID];  // validation failure w/ version <= 4.3
    te_outDir[gl_InvocationID] = tc_outDir[gl_InvocationID];
}
