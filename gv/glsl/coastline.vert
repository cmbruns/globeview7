const int WGS84_PROJECTION = 1;
const int ORTHOGRAPHIC_PROJECTION = 2;

in vec2 in_pos;
layout(location = 2) uniform mat3 obq_X_ecf = mat3(1);
layout(location = 4) uniform int projection = WGS84_PROJECTION;

void main() {
    // Input data is in WGS84
    vec2 wgs = radians(in_pos);
    vec3 ecf = vec3(
        cos(wgs.x) * cos(wgs.y),
        sin(wgs.x) * cos(wgs.y),
        sin(wgs.y));

    vec3 obq = obq_X_ecf * ecf;

    vec3 nmc = vec3(0);
    if (projection == WGS84_PROJECTION) {
        vec2 prj = vec2(
            atan(obq.y, obq.x),
            asin(obq.z)
        );
        nmc = vec3(prj, 1);
    }
    else {  // ORTHOGRAPHIC_PROJECTION
        nmc = vec3(
            obq.y,
            obq.z,
            1);
    }

    gl_Position = vec4(nmc.xyz, 1);
}
