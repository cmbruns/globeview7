#pragma include "projection.glsl"

layout (lines) in;
layout (triangle_strip, max_vertices = 6) out;  // polygon representing a line segment

uniform float uLineWidth = 2.0;

in vec4 gColor[];
out vec4 fColor;

void main()
{
    fColor = gColor[0];

    vec2 ndc0 = ndc_for_obq(gl_in[0].gl_Position.xyz).xy;
    vec2 ndc1 = ndc_for_obq(gl_in[1].gl_Position.xyz).xy;

    vec3 offset_win = vec3(uLineWidth / 2, uLineWidth / 2, 0);
    vec2 offset_ndc = ndc_for_win(offset_win).xy;

    // local coordinate system of line segment
    vec2 u_hat = normalize(ndc1 - ndc0);
    vec2 v_hat = vec2(u_hat.y, -u_hat.x);

    // distance from center to edge
    vec2 du = u_hat * offset_ndc;
    vec2 dv = v_hat * offset_ndc;

    gl_Position = vec4(ndc0-du, 0, 1); EmitVertex(); // pointy tip of end cap left of p0
    gl_Position = vec4(ndc0+dv, 0, 1); EmitVertex(); // above p0
    gl_Position = vec4(ndc0-dv, 0, 1); EmitVertex(); // below p0
    gl_Position = vec4(ndc1+dv, 0, 1); EmitVertex(); // above p1
    gl_Position = vec4(ndc1-dv, 0, 1); EmitVertex(); // below p1
    gl_Position = vec4(ndc1+du, 0, 1); EmitVertex(); // pointy tip of end cap right of p1

    EndPrimitive();
}
