#pragma include "projection.glsl"

uniform vec4 uColor = vec4(0, 0, 1, 0.3);
in vec3 nmc;
out vec4 fColor;

void main()
{
    mat3 ndc_X_nmc = mat3(ub.ndc_X_nmc4);
    vec3 ndc = ndc_X_nmc * nmc;
    gl_Position = vec4(ndc.xy, 0, ndc.z);
    fColor = uColor;
}
