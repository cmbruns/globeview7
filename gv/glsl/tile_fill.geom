#pragma include "projection.glsl"

layout (lines) in;
uniform vec3 uFirstPoint_ecf;
layout (triangle_strip, max_vertices = 3) out;  // one triangle

in vec4 gColor[];
out vec4 fColor;

void main()
{
    fColor = gColor[0];  // 0: use color of first point in the line segment

    vec3 obqFirst = obq_for_ecf(uFirstPoint_ecf);
    clip_obq_point(obqFirst);  // push to horizon if needed

    vec2 ndcFirst = ndc_for_obq(obqFirst).xy;
    vec2 ndc0 = ndc_for_obq(gl_in[0].gl_Position.xyz).xy;
    vec2 ndc1 = ndc_for_obq(gl_in[1].gl_Position.xyz).xy;

    // always put first corner of triangle at first point of vertex buffer
    gl_Position = vec4(ndcFirst, 0, 1); EmitVertex();
    gl_Position = vec4(ndc0, 0, 1); EmitVertex();
    gl_Position = vec4(ndc1, 0, 1); EmitVertex();

    EndPrimitive();
}
