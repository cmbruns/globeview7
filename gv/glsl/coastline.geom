const int WGS84_PROJECTION = 1;
const int ORTHOGRAPHIC_PROJECTION = 2;

// Clip line segments that go around the WGS84 seam
// TODO: interpolate curves

layout (lines) in;
layout (line_strip, max_vertices = 36) out;  // 36 = 2-per-segment * 2-for-seam-crossing * 9 worlds shown
layout(location = 1) uniform mat3 ndc_X_nmc = mat3(1);
layout(location = 3) uniform mat3 nmc_X_ndc = mat3(1);
layout(location = 4) uniform int projection = WGS84_PROJECTION;

out vec4 color;

const float pi = 3.14159265359;
const float two_pi = 2 * pi;

void drawWgsSegment(in vec3 nmc0, in vec3 nmc1)
{
    // Does the longitude range need to be duplicated?
    // TODO: compute this range on the host
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
    // earth longitude range for GCS is 2pi in nmc units
    int inmc_xmin = int(floor((nmc_xmin + pi) / two_pi));
    int inmc_xmax = int(ceil((nmc_xmax - pi) / two_pi));

    // show at most 9 worlds
    if ((inmc_xmax - inmc_xmin) > 8 * two_pi) {
        inmc_xmin = -4;
        inmc_xmax = 4;
    }

    for (int nmcx_offset = inmc_xmin; nmcx_offset <= inmc_xmax; nmcx_offset += 1)
    {
        vec3 offset = vec3(two_pi * nmcx_offset, 0, 0);
        vec3 ndc0 = ndc_X_nmc * (nmc0 + offset);
        vec3 ndc1 = ndc_X_nmc * (nmc1 + offset);
        gl_Position = vec4(ndc0.xy, 0, 1);
        EmitVertex();
        gl_Position = vec4(ndc1.xy, 0, 1);
        EmitVertex();
        EndPrimitive();
    }
}

void main()
{
    vec3 nmc0 = gl_in[0].gl_Position.xyz;
    vec3 nmc1 = gl_in[1].gl_Position.xyz;
    color = vec4(0.03, 0.34, 0.60, 1);

    if (abs(nmc1.x - nmc0.x) > 2)// segment crosses seam
    {
        // Enforce left to right for simpler clipping
        vec3 left = nmc0;
        vec3 right = nmc1;
        if (left.x > right.x) {
            left = nmc1;
            right = nmc0;
        }
        float alpha = (left.x + pi) / (left.x + pi + pi - right.x);
        vec3 mid = vec3(-pi, mix(left.yz, right.yz, alpha));
        drawWgsSegment(left, mid);
        mid.x = pi;
        drawWgsSegment(mid, right);
    }
    else
    {
        drawWgsSegment(nmc0, nmc1);
    }
}
