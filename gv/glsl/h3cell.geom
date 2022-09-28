layout (lines) in;
layout (lines, max_vertices = 4) out;  // up to two line segments

void main()
{
    Segment obq = Segment(gl_in[0].gl_Position.xyz);
    Segment result[2];
    int seg_count = clip_obq_segment(obq, projection, result);
}
