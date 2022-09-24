// requires version.glsl, projection.glsl
layout(location = 1) uniform mat3 ndc_X_nmc = mat3(1);
out vec3 nmc;

void main() {
    // TODO: maybe bounds should be handled on the host side
    nmc = equirectBounds_nmc[gl_VertexID];  // needs projection.glsl
    vec3 ndc = ndc_X_nmc * nmc;
    gl_Position = vec4(ndc.xy, 0, ndc.z);
}
