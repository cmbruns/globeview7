struct Waypoint3 {
    vec3 p;  // location of the waypoint
    vec3 inDir;  // unit direction into the waypoint
    vec3 outDir;  // unit direction out of the waypoint
};

struct PathSegment3 {
    Waypoint3 wp0;
    Waypoint3 wp1;
};
