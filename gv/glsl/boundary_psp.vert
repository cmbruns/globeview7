in vec3 nmc;

void main()
{
    float v = ub.view_height_radians;
    float radius = sqrt(v / (2 + v));
    mat3 ndc_X_nmc = mat3(ub.ndc_X_nmc4);
    vec3 ndc = ndc_X_nmc * nmc;
    gl_Position = vec4(radius * ndc.xy, 0, ndc.z);
}
