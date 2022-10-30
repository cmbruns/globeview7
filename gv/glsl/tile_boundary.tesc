#line 2
layout (vertices = 2) out;

in vec3 tc_inDir[];
in vec3 tc_outDir[];

out vec3 te_inDir[];
out vec3 te_outDir[];

void main() {
    if (gl_InvocationID == 0)
    {
        gl_TessLevelOuter[0] = 1.0;  // Number of lines
        gl_TessLevelOuter[1] = 5.0;  // Number of segments per line
    }
    gl_out[gl_InvocationID].gl_Position = gl_in[gl_InvocationID].gl_Position;

    // te_inDir[gl_InvocationID] = tc_inDir[gl_InvocationID];  // validation failure!?
    // outDir_te[gl_InvocationID] = outDir_ecf[gl_InvocationID];
    // outDir_tese[gl_InvocationID] = vec3(0, 1, 0);
}
