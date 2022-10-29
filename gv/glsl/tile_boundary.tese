layout (isolines) in;

void main() {
    float t = gl_TessCoord.x;
    // TODO: "normalize" is not the correct interpolation
    vec3 ecf = normalize(t * gl_in[0].gl_Position.xyz +
        (1 - t) * gl_in[1].gl_Position.xyz);
    mat3 obq_X_ecf = mat3(ub.obq_X_ecf4);
    vec3 obq = obq_X_ecf * ecf;
    vec3 nmc = nmc_for_obq(obq);
    mat3 ndc_X_nmc = mat3(ub.ndc_X_nmc4);
    vec3 ndc = ndc_X_nmc * nmc;
    gl_Position = vec4(ndc, 1);
}
