#pragma include "waypoint.glsl"
#pragma include "projection.glsl"

layout (isolines) in;

in vec3 te_inDir[];
in vec3 te_outDir[];
in Waypoint3 te_waypoint_obq[];
in vec4 teColor[];

out vec4 gColor;

void main()
{
    gColor = teColor[0];

    // Transform positions and direction to obq units
    Waypoint3 wp0 = te_waypoint_obq[0];
    Waypoint3 wp1 = te_waypoint_obq[1];
    vec3 p0 = wp0.p;
    vec3 p1 = wp1.p;

    float s = length(p1 - p0);
    vec3 m0 = s * wp0.outDir;
    vec3 m1 = s * wp1.inDir;

    // Interpolate coordinates
    float t = gl_TessCoord.x;
    // Cubic hermite spline
    vec3 obq = (2*t*t*t - 3*t*t + 1) * p0
        + (t*t*t - 2*t*t + t) * m0
        + (-2*t*t*t + 3*t*t) * p1
        + (t*t*t - t*t) * m1;

    gl_Position = vec4(normalize(obq), 1);
}
