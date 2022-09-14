layout (lines_adjacency) in;
layout (line_strip, max_vertices = 4) out;

void main() {
    gl_Position = gl_in[1].gl_Position;
    EmitVertex();
}
