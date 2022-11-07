#ifndef CUSTOM_PROCESS_INCLUDES
#extension GL_GOOGLE_include_directive : enable
#include "projection.glsl"
#endif

uniform vec4 uColor = vec4(0, 1, 1, 1);

in vec2 wgs;  // longitude, latitude in WGS84 radians
out vec4 gColor;

void main() {
    vec3 ecf = ecf_for_wgs(wgs);  // geocentric x, y, z in radians
    mat3 obq_X_ecf = mat3(ub.obq_X_ecf4);
    vec3 obq = obq_X_ecf * ecf;  // geocentric recentered to map center
    gl_Position = vec4(obq, 1);
    gColor = uColor;
}
