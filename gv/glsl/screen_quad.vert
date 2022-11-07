#ifndef CUSTOM_PROCESS_INCLUDES
#extension GL_GOOGLE_include_directive : enable
#include "projection.glsl"
#endif

// call with GL.glDrawArrays(GL.GL_TRIANGLE_FAN, 0, 4)

uniform vec4 uColor = vec4(0, 0, 1, 0.3);
out Data { vec4 color; };
out vec3 nmc;  // for use by base map shader

const vec4 corner[] = vec4[](
    vec4(-1, +1, 0.5, 1),
    vec4(+1, +1, 0.5, 1),
    vec4(+1, -1, 0.5, 1),
    vec4(-1, -1, 0.5, 1));

void main()
{
    gl_Position = corner[gl_VertexID];
    color = uColor;
    nmc = nmc_for_ndc(corner[gl_VertexID].xyw);
}
