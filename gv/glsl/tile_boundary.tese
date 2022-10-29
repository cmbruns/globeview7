layout (isolines) in;

void main() {
    float u = gl_TessCoord.x;
    gl_Position =
        u * gl_in[0].gl_Position +
        (1 - u) * gl_in[1].gl_Position;
}
