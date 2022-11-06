#ifndef CUSTOM_PROCESS_INCLUDES
#extension GL_GOOGLE_include_directive : enable
#include "projection.glsl"
#endif

uniform vec4 uColor = vec4(0.03, 0.34, 0.60, 1);
uniform float uScale = 1.0;

in vec3 nmc;

out Data { vec4 color; };

void main()
{
    mat3 ndc_X_nmc = mat3(ub.ndc_X_nmc4);
    vec3 ndc = ndc_X_nmc * nmc;
    gl_Position = vec4(uScale * ndc.xy, 0, ndc.z);
    color = uColor;
}
