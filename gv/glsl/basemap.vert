#ifndef CUSTOM_PROCESS_INCLUDES
#extension GL_GOOGLE_include_directive : enable
#include "projection.glsl"
#endif

in vec3 nmc_in;

out vec3 nmc;

void main() {
    nmc = nmc_in;
    mat3 ndc_X_nmc = mat3(ub.ndc_X_nmc4);
    vec3 ndc = ndc_X_nmc * nmc;
    gl_Position = vec4(ndc.xy, 0, ndc.z);
}
