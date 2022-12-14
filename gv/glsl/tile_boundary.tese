#ifndef CUSTOM_PROCESS_INCLUDES
#extension GL_GOOGLE_include_directive : enable
#include "waypoint.glsl"
#include "projection.glsl"
#endif

layout (isolines) in;

in Waypoint3 te_waypoint_obq[];
patch in Waypoint3 midPoint;
patch in float midT;

in Data { vec4 color; } tese_input[];
out Data { vec4 color; } tese_output;

void main()
{
    tese_output.color = tese_input[0].color;

    // Interpolate curved segment
    // TODO: handle specially bisected segments
    Waypoint3 wp0 = te_waypoint_obq[0];
    Waypoint3 mid = midPoint;
    Waypoint3 wp1 = te_waypoint_obq[1];
    float t = gl_TessCoord.x;
    Waypoint3 wp;
    if (t <= midT) {
        wp = interpolateWaypoint(wp0, mid, t / midT);
        // tese_output.color = vec4(1, 0, 0, 1);
    }
    else {
        wp = interpolateWaypoint(mid, wp1, (t - midT) / (1 - midT));
        // tese_output.color = vec4(0, 0, 1, 1);
    }

    gl_Position = vec4(normalize(wp.p), 1);
}
