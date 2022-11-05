#ifndef CUSTOM_PROCESS_INCLUDES
#extension GL_GOOGLE_include_directive : enable
#include "waypoint.glsl"
#include "projection.glsl"
#endif

layout (isolines) in;

in Waypoint3 te_waypoint_obq[];
patch in vec4 teColor;

out vec4 gColor;

void main()
{
    gColor = teColor;

    // Interpolate curved segment
    // TODO: handle specially bisected segments
    Waypoint3 wp0 = te_waypoint_obq[0];
    Waypoint3 wp1 = te_waypoint_obq[2];
    float t = gl_TessCoord.x;
    Waypoint3 mid = interpolateWaypoint(wp0, wp1, t);

    gl_Position = vec4(normalize(mid.p), 1);
}
