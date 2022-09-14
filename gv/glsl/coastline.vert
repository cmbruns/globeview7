in vec2 in_pos;

layout(location = 2) uniform mat3 obq_X_ecf = mat3(1);

void main() {
    vec2 wgs = radians(in_pos);
    vec3 ecf = vec3(
        cos(wgs.x) * cos(wgs.y),
        sin(wgs.x) * cos(wgs.y),
        sin(wgs.y)
    );
    vec3 obq = obq_X_ecf * ecf;
    vec2 prj = vec2(
        atan(obq.y, obq.x),
        asin(obq.z)
    );

    vec3 nmc = vec3(prj / radians(90), 1);
    gl_Position = vec4(nmc.xyz, 1);
}
