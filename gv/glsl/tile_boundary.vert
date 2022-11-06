#ifndef CUSTOM_PROCESS_INCLUDES
#extension GL_GOOGLE_include_directive : enable
#include "waypoint.glsl"
#include "projection.glsl"
#endif

layout (location = 0) in vec3 pos_ecf_in;  // vertex position
layout (location = 1) in vec3 v_inDir;  // vertex incoming direction
layout (location = 2) in vec3 v_outDir;  // vertex outgoing direction

uniform vec4 uColor = vec4(1, 0, 1, 1);  // magenta means someone needs to set that color...
out Data { vec4 color; };
out Waypoint3 tc_waypoint_obq;

void main()
{
    vec3 obq = obq_for_ecf(pos_ecf_in);
    gl_Position = vec4(obq, 1);
    color = uColor;
    tc_waypoint_obq = Waypoint3(
        obq,
        obq_for_ecf(v_inDir),
        obq_for_ecf(v_outDir));
}
