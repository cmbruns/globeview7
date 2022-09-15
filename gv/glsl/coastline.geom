// Discard line segments that go around the WGS84 seam
// TODO: clip the lines to the seam
// TODO: interpolate curves

layout (lines) in;
layout (line_strip, max_vertices = 36) out;  // 2-per-segment * 2-for-seam-crossing * 9 worlds shown
layout(location = 1) uniform mat3 ndc_X_nmc = mat3(1);
layout(location = 3) uniform mat3 nmc_X_ndc = mat3(1);

out vec4 color;

void main() {
    vec3 nmc0 = gl_in[0].gl_Position.xyz;
    vec3 nmc1 = gl_in[1].gl_Position.xyz;
    if (abs(nmc0.x - nmc1.x) > 2)// segment crosses seam
        return;// skip this segment for now...  TODO: clip it

    // Does the longitude range need to be duplicated?
    float nmc_xmin = 0;
    float nmc_xmax = 0;
    const vec3 corners_ndc[4] = vec3[4](
        vec3(-1, -1, 0),
        vec3(-1,  1, 0),
        vec3( 1, -1, 0),
        vec3( 1,  1, 0));
    for (int c = 0; c < 4; ++c) {
        vec3 nmc = nmc_X_ndc * corners_ndc[c];
        nmc_xmin = min(nmc_xmin, nmc.x);
        nmc_xmax = max(nmc_xmax, nmc.x);
    }
    // earth longitude range for GCS is 4.0 in nmc units
    int inmc_xmin = int(floor((nmc_xmin + 2) / 4.0)) * 4;
    int inmc_xmax = int(ceil((nmc_xmax - 2) / 4.0)) * 4;

    // show at most 9 worlds
    if ((inmc_xmax - inmc_xmin) > 8 * 4) {
        inmc_xmin = -16;
        inmc_xmax = 16;
    }

    for (int nmcx_offset = inmc_xmin; nmcx_offset <= inmc_xmax; nmcx_offset += 4)
    {
        vec3 offset = vec3(nmcx_offset, 0, 0);
        vec3 ndc0 = ndc_X_nmc * (nmc0 + offset);
        vec3 ndc1 = ndc_X_nmc * (nmc1 + offset);
        gl_Position = vec4(ndc0.xy, 0, 1);
        EmitVertex();
        gl_Position = vec4(ndc1.xy, 0, 1);
        EmitVertex();
        EndPrimitive();
    }
}
