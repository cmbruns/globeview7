#line 2
#pragma include "waypoint.glsl"
#pragma include "projection.glsl"

layout (location = 0) in vec3 pos_ecf_in;  // vertex position
layout (location = 1) in vec3 v_inDir;  // vertex incoming direction
layout (location = 2) in vec3 v_outDir;  // vertex outgoing direction

uniform vec4 uColor = vec4(1, 0, 1, 1);  // magenta means someone needs to set that color...
out vec4 fColor;

out vec3 tc_inDir;
out vec3 tc_outDir;
out Waypoint3 tc_waypoint_ecf;

void main()
{
    gl_Position = vec4(pos_ecf_in, 1);
    fColor = uColor;
    tc_waypoint_ecf = Waypoint3(
        pos_ecf_in,
        v_inDir,
        v_outDir);

    tc_inDir = v_inDir;
    tc_outDir = v_outDir;
}
