#pragma include "projection.glsl"

layout (lines) in;
layout (triangle_strip, max_vertices = 3) out;  // one triangle

in Data { vec4 color; } geom_input[];
out Data { vec4 color; } geom_output;

void main()
{
    geom_output.color = geom_input[0].color;  // 0: use color of first point in the line segment

    vec2 ndc0 = gl_in[0].gl_Position.xy;
    vec2 ndc1 = gl_in[1].gl_Position.xy;

    vec2 ndcZero = vec2(0, 0);

    // always put first corner of triangle at center of display
    gl_Position = vec4(ndcZero, 0, 1); EmitVertex();
    gl_Position = vec4(ndc0, 0, 1); EmitVertex();
    gl_Position = vec4(ndc1, 0, 1); EmitVertex();

    EndPrimitive();
}
