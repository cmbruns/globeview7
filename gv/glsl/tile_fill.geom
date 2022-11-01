#line 2

layout (lines) in;
layout (location = 8) uniform vec3 uFirstPoint_ecf;
layout (triangle_strip, max_vertices = 3) out;  // one triangle

out vec4 outColor;

void main()
{
    outColor = vec4(1, 1, 0, 0.3);

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
