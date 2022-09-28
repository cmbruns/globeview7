#line 2

layout (lines) in;
layout (line_strip, max_vertices = 4) out;  // up to two line segments

uniform mat3 ndc_X_nmc = mat3(1);
uniform int projection = EQUIRECTANGULAR_PROJECTION;

void main()
{
    Segment3 obq = Segment3(gl_in[0].gl_Position.xyz, gl_in[1].gl_Position.xyz);

    // some projections e.g. orthographic like to clip in obq space
    Segment3 clipped;
    int obq_seg_count = clip_obq_segment(obq, projection, clipped);
    if (obq_seg_count < 1)
        return;

    Segment3 nmc = Segment3(
        nmc_for_obq(clipped.p1, projection),
        nmc_for_obq(clipped.p2, projection));

    // some projections e.g. equirectangular like to clip in nmc space
    Segment3 clipped2[2];
    int nmc_seg_count = clip_nmc_segment(nmc, projection, clipped2);
    if (nmc_seg_count < 1)
        return;

    for (int s = 0; s < nmc_seg_count; ++s)
    {
        Segment3 c2 = clipped2[s];
        Segment3 ndc = Segment3(
        ndc_X_nmc * c2.p1, ndc_X_nmc * c2.p2);
        gl_Position = vec4(ndc.p1.xy, 0, 1);
        EmitVertex();
        gl_Position = vec4(ndc.p2.xy, 0, 1);
        EmitVertex();
        EndPrimitive();
    }
}
