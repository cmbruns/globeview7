#line 2
layout (isolines) in;

in vec3 te_inDir[];
in vec3 te_outDir[];

out vec4 outColor;

vec2 ndc_for_ecf_dir(in vec3 pos_ecf, in vec3 direction_ecf, out vec2 direction_ndc)
{
    mat3 obq_X_ecf = mat3(ub.obq_X_ecf4);
    vec3 obq = obq_X_ecf * pos_ecf;
    vec3 nmc = nmc_for_obq(obq);
    mat3 ndc_X_nmc = mat3(ub.ndc_X_nmc4);
    vec3 ndc = ndc_X_nmc * nmc;

    vec3 dobq = obq_X_ecf * direction_ecf;
    vec2 dnmc = dnmc_for_dobq(dobq, obq);
    direction_ndc = normalize((ndc_X_nmc * vec3(dnmc, 1)).xy);

    return ndc.xy / ndc.z;
}

void main()
{
    outColor = vec4(1, 0, 0, 1);  // red

    // Transform positions and direction to ndc units
    vec2 dndc0;
    vec2 dndc1;
    vec2 p0 = ndc_for_ecf_dir(gl_in[0].gl_Position.xyz, te_outDir[0], dndc0);
    vec2 p1 = ndc_for_ecf_dir(gl_in[1].gl_Position.xyz, te_inDir[1], dndc1);

    float s = length(p1 - p0);
    vec2 m0 = s * dndc0;
    vec2 m1 = s * dndc1;

    // Interpolate coordinates
    float t = gl_TessCoord.x;
    // vec2 ndc = t * ndc0 + (1 - t) * ndc1;  // Linear interpolation
    // Cubic hermite spline
    vec2 ndc = (2*t*t*t - 3*t*t + 1) * p0
        + (t*t*t - 2*t*t + t) * m0
        + (-2*t*t*t + 3*t*t) * p1
        + (t*t*t - t*t) * m1;

    gl_Position = vec4(ndc, 0, 1);
}
