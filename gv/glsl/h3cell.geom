#pragma include "projection.glsl"

layout (lines) in;
layout (line_strip, max_vertices = 4) out;  // up to two line segments

in vec4 gColor[];
out vec4 fColor;

void main()
{
    fColor = gColor[0];

    Segment3 obq = Segment3(gl_in[0].gl_Position.xyz, gl_in[1].gl_Position.xyz);

    // some projections e.g. orthographic like to clip in obq space
    Segment3 clipped;
    int obq_seg_count = clip_obq_segment(obq, clipped);
    if (obq_seg_count < 1)
        return;

    Segment3 nmc = Segment3(
        nmc_for_obq(clipped.p1),
        nmc_for_obq(clipped.p2));

    // some projections e.g. equirectangular like to clip in nmc space
    Segment3 clipped2[2];
    int nmc_seg_count = clip_nmc_segment(nmc, clipped2);
    if (nmc_seg_count < 1)
        return;

    mat3 ndc_X_nmc = mat3(ub.ndc_X_nmc4);
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
