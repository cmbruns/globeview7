#line 2
#pragma include "projection.glsl"
layout (isolines) in;

in vec3 te_inDir[];
in vec3 te_outDir[];

void main()
{
    // Transform positions and direction to obq units
    vec3 p0 = gl_in[0].gl_Position.xyz;
    vec3 p1 = gl_in[1].gl_Position.xyz;

    float s = length(p1 - p0);
    vec3 m0 = s * te_outDir[0];
    vec3 m1 = s * te_inDir[1];

    // Interpolate coordinates
    float t = gl_TessCoord.x;
    // Cubic hermite spline
    vec3 obq = (2*t*t*t - 3*t*t + 1) * p0
        + (t*t*t - 2*t*t + t) * m0
        + (-2*t*t*t + 3*t*t) * p1
        + (t*t*t - t*t) * m1;

    gl_Position = vec4(normalize(obq), 1);
}
