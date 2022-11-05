struct Waypoint3 {
    vec3 p;  // location of the waypoint
    vec3 inDir;  // unit direction into the waypoint
    vec3 outDir;  // unit direction out of the waypoint
};

Waypoint3 interpolateWaypoint(in Waypoint3 w0, in Waypoint3 w1, in float t)
{
    float s = length(w1.p - w0.p);
    vec3 m0 = s * w0.outDir;
    vec3 m1 = s * w1.inDir;
    // Cubic hermite spline
    // Location p
    vec3 p = (2*t*t*t - 3*t*t + 1) * w0.p
        + (t*t*t - 2*t*t + t) * m0
        + (-2*t*t*t + 3*t*t) * w1.p
        + (t*t*t - t*t) * m1;
    // Direction m
    vec3 m = normalize(
        (6*t*t - 6*t) * w0.p
        + (3*t*t - 4*t + 1) * m0
        + (-6*t*t + 6*t) * w1.p
        + (3*t*t - 2*t) * m1);
    Waypoint3 result = Waypoint3(p, m, m);  // smooth continuous inDir==outDir
    return result;
}

struct PathSegment3 {
    Waypoint3 wp0;
    Waypoint3 wp1;
};
