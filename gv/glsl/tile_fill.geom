#pragma include "projection.glsl"

layout (lines) in;
layout (location = 8) uniform vec3 uFirstPoint_ecf;
layout (triangle_strip, max_vertices = 3) out;  // one triangle

in vec4 gColor[];
out vec4 fColor;

void main()
{
    fColor = gColor[0];

    vec3 ndcFirst = ndc_for_ecf(uFirstPoint_ecf);
    vec3 ndc0 = ndc_for_obq(gl_in[0].gl_Position.xyz);
    vec3 ndc1 = ndc_for_obq(gl_in[1].gl_Position.xyz);

    // always put first corner of triangle at first point of vertex buffer
    gl_Position = vec4(ndcFirst.xy, 0, 1);
    EmitVertex();
    gl_Position = vec4(ndc0.xy, 0, 1);
    EmitVertex();
    gl_Position = vec4(ndc1.xy, 0, 1);
    EmitVertex();
    EndPrimitive();
}
