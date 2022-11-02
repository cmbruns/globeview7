#line 2
#pragma include "projection.glsl"

layout (vertices = 2) out;

in vec3 tc_inDir[];
in vec3 tc_outDir[];

out vec3 te_inDir[];
out vec3 te_outDir[];


float sine2DAngle(vec2 v1, vec2 v2)
{
    return abs(cross(vec3(v1, 0), vec3(v2, 0)).z);
}


void main()
{
    if (gl_InvocationID == 0)
    {
        gl_TessLevelOuter[0] = 1.0;  // Number of lines

        // dynamically determine tessellation level
        vec3 ecf0 = gl_in[0].gl_Position.xyz;
        vec3 ecf1 = gl_in[1].gl_Position.xyz;
        vec3 win0 = win_for_ecf(ecf0);
        vec3 win1 = win_for_ecf(ecf1);
        vec2 dw = (win1 - win0).xy;
        float lw = length(dw);
        float nsegs = 1;  // minimum number of interpolated segments
        nsegs += lw / 15;  // more segments for longer lines
        if (lw > 0) {
            vec2 lineDir = dw / lw;
            vec2 m0 = normalize(dwin_for_decf(tc_outDir[0], ecf0));
            vec2 m1 = normalize(dwin_for_decf(tc_inDir[1], ecf1));
            float c0 = 1 - dot(m0, lineDir);  // 1 minus cosine of slope angle wrt line
            float c1 = 1 - dot(m1, lineDir);
            float cmax = max(c0, c1);  // range 0 to 2
            nsegs += 100 * cmax;  // more segments for more dramatic curves
        }

        gl_TessLevelOuter[1] = nsegs;  // Number of segments per line
    }
    gl_out[gl_InvocationID].gl_Position = gl_in[gl_InvocationID].gl_Position;
    te_inDir[gl_InvocationID] = tc_inDir[gl_InvocationID];  // validation failure w/ version <= 4.3
    te_outDir[gl_InvocationID] = tc_outDir[gl_InvocationID];
}
