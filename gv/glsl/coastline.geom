// Clip line segments that go around the WGS84 seam
// TODO: interpolate curves

layout (lines) in;
layout (line_strip, max_vertices = 36) out;  // 36 = 2-per-segment * 2-for-seam-crossing * 9 worlds shown
layout(location = 1) uniform mat3 ndc_X_nmc = mat3(1);
layout(location = 2) uniform mat3 obq_X_ecf = mat3(1);
layout(location = 3) uniform mat3 nmc_X_ndc = mat3(1);
layout(location = 4) uniform int projection = EQUIRECTANGULAR_PROJECTION;

out vec4 color;

void drawSegment(in vec3 nmc0, in vec3 nmc1)
{
    int inmc_xmin = 0;
    int inmc_xmax = 0;
    
    if (projection == EQUIRECTANGULAR_PROJECTION)
    {
        // Does the longitude range need to be duplicated?
        // TODO: compute this range on the host
        float nmc_xmin = 0;
        float nmc_xmax = 0;
        const vec3 corners_ndc[4] = vec3[4](
            vec3(-1, -1, 0),
            vec3(-1, 1, 0),
            vec3(1, -1, 0),
            vec3(1, 1, 0));
        for (int c = 0; c < 4; ++c) {
            vec3 nmc = nmc_X_ndc * corners_ndc[c];
            nmc_xmin = min(nmc_xmin, nmc.x);
            nmc_xmax = max(nmc_xmax, nmc.x);
        }
        // earth longitude range for GCS is 2pi in nmc units
        inmc_xmin = int(floor((nmc_xmin + pi) / two_pi));
        inmc_xmax = int(ceil((nmc_xmax - pi) / two_pi));

        // show at most 9 worlds
        if ((inmc_xmax - inmc_xmin) > 8 * two_pi) {
            inmc_xmin = -4;
            inmc_xmax = 4;
        }
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

vec3 obq_for_wgs_deg(in vec2 wgs_deg) {
    vec2 wgs = radians(wgs_deg);
    vec3 ecf = ecf_for_wgs(wgs);
    vec3 obq = obq_X_ecf * ecf;
    return obq;
}

void main()
{
    vec2 wgs_deg0 = gl_in[0].gl_Position.xy;
    vec2 wgs_deg1 = gl_in[1].gl_Position.xy;

    // Hack to remove antarctica lines in coastline database
    if (wgs_deg0.y == -90)
       return;
    if (wgs_deg1.y == -90)
       return;
    if (wgs_deg0.x == 180 && wgs_deg1.x == 180)
        return;
    if (wgs_deg0.x == -180 && wgs_deg1.x == -180)
        return;

    vec3 obq0 = obq_for_wgs_deg(wgs_deg0);
    vec3 obq1 = obq_for_wgs_deg(wgs_deg1);

    if (cull_obq(obq0, projection) && cull_obq(obq1, projection))
        return;

    Segment3 nmc = Segment3(
        nmc_for_obq(obq0, projection),
        nmc_for_obq(obq1, projection));
    Segment3 nmc_clipped[2];
    int nmc_seg_count = clip_nmc_segment(nmc, projection, nmc_clipped);
    if (nmc_seg_count < 1)
        return;

    color = vec4(0.03, 0.34, 0.60, 1);

    for (int s = 0; s < nmc_seg_count; ++s) {
        Segment3 nmcc = nmc_clipped[s];
        drawSegment(nmcc.p1, nmcc.p2);
    }
}
