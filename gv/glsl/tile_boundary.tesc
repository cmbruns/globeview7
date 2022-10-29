layout (vertices = 2) out;

void main() {
    if (gl_InvocationID == 0)
    {
        gl_TessLevelOuter[0] = 1.0;  // Number of lines
        gl_TessLevelOuter[1] = 5.0;  // Number of segments per line
    }
    gl_out[gl_InvocationID].gl_Position = gl_in[gl_InvocationID].gl_Position;
}
