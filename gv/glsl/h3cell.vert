#pragma include "projection.glsl"  // must be done manually at the moment...
#line 3

in vec2 wgs;  // longitude, latitude in WGS84 radians
uniform mat3 obq_X_ecf = mat3(1);

void main() {
    vec3 ecf = ecf_for_wgs(wgs);  // geocentric x, y, z in radians
    vec3 obq = obq_X_ecf * ecf;  // geocentric recentered to map center
    gl_Position = vec4(obq, 1);
}
