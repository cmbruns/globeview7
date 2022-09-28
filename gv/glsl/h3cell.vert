in vec2 corner;
uniform mat3 obq_X_ecf = mat3(1);
uniform mat3 ndc_X_nmc = mat3(1);
uniform int projection = EQUIRECTANGULAR_PROJECTION;

void main() {
    // swap x,y because h3 returns lat/lng, not lng/lat
    vec2 wgs = radians(corner.yx);  // WGS84 longitude, latitude in radians
    vec3 ecf = ecf_for_wgs(wgs);  // geocentric x, y, z in radians
    vec3 obq = obq_X_ecf * ecf;  // geocentric recentered to map center
    // TODO: gnomonic edge direction from obq coordinates
    vec3 nmc = nmc_for_obq(obq, projection);  // normalized map coordinates
    vec3 ndc = ndc_X_nmc * nmc;  // OpenGL convention normalized device coordinates
    gl_Position = vec4(ndc.xy, 0, ndc.z);
}
