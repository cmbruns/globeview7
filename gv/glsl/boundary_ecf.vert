in vec3 ecf;

void main()
{
    mat3 obq_X_ecf = mat3(ub.obq_X_ecf4);
    vec3 obq = obq_X_ecf * ecf;
    vec3 nmc = nmc_for_obq(obq);
    mat3 ndc_X_nmc = mat3(ub.ndc_X_nmc4);
    vec3 ndc = ndc_X_nmc * nmc;
    gl_Position = vec4(ndc.xy, 0, ndc.z);
}
