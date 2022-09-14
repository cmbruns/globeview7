// Discard line segments that go around the WGS84 seam
// TODO: clip the lines to the seam
// TODO: interpolate curves

layout (lines) in;
layout (line_strip, max_vertices = 4) out;
layout(location = 1) uniform mat3 ndc_X_nmc = mat3(1);

out vec4 color;

void main() {
    vec3 nmc0 = gl_in[0].gl_Position.xyz;
    vec3 ndc0 = ndc_X_nmc * nmc0;
    vec3 nmc1 = gl_in[1].gl_Position.xyz;
    vec3 ndc1 = ndc_X_nmc * nmc1;
    color = vec4(0.03, 0.34, 0.60, 1);
    if (abs(nmc0.x - nmc1.x) > 1)  // segment crosses seam
    {
        color = vec4(1, 0, 0, 1);
        return;  // skip this segment for now...  TODO: clip it
    }
    gl_Position = vec4(ndc0.xy, 0, 1);
    EmitVertex();
    gl_Position = vec4(ndc1.xy, 0, 1);
    EmitVertex();
    EndPrimitive();
}
