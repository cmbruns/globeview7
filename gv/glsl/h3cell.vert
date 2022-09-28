const int WGS84_PROJECTION = 0;
const int ORTHOGRAPHIC_PROJECTION = 1;

in vec2 corner;
uniform mat3 obq_X_ecf = mat3(1);
uniform mat3 ndc_X_nmc = mat3(1);
uniform int projection = WGS84_PROJECTION;

void main() {
    vec2 wgs = radians(corner.yx);
    vec3 ecf = vec3(
        cos(wgs.x) * cos(wgs.y),
        sin(wgs.x) * cos(wgs.y),
        sin(wgs.y));
    vec3 obq = obq_X_ecf * ecf;
    // TODO: gnomonic edge direction
    vec3 nmc;
    if (projection == WGS84_PROJECTION) {
        nmc = vec3(atan(obq.y, obq.x), asin(obq.z), 1);
    }
    else {
        // orthographic
        nmc = vec3(obq.y, obq.z, 1);
    }
    // TODO: other projection
    vec3 ndc = ndc_X_nmc * nmc;
    gl_Position = vec4(ndc.xy, 0, ndc.z);
}
