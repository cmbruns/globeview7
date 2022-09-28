in vec2 corner;
uniform mat3 obq_X_ecf = mat3(1);
uniform mat3 ndc_X_nmc = mat3(1);
uniform int projection = EQUIRECTANGULAR_PROJECTION;

void main() {
    vec2 wgs = radians(corner.yx);
    vec3 ecf = vec3(
        cos(wgs.x) * cos(wgs.y),
        sin(wgs.x) * cos(wgs.y),
        sin(wgs.y));
    vec3 obq = obq_X_ecf * ecf;
    // TODO: gnomonic edge direction
    vec3 nmc = nmc_for_obq(obq, projection);
    vec3 ndc = ndc_X_nmc * nmc;
    gl_Position = vec4(ndc.xy, 0, ndc.z);
}
