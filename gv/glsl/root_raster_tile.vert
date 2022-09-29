// requires version.glsl, projection.glsl
out vec3 nmc;

void main() {
    // TODO: maybe bounds should be handled on the host side
    nmc = equirectBounds_nmc[gl_VertexID];  // needs projection.glsl
    mat3 ndc_X_nmc = mat3(ub.ndc_X_nmc4);
    vec3 ndc = ndc_X_nmc * nmc;
    gl_Position = vec4(ndc.xy, 0, ndc.z);
}
