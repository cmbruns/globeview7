in vec2 lonlat_deg;

void main() {
    // keep values in degrees to permit exact matching in coastline cleanup
    gl_Position = vec4(lonlat_deg, 0, 1);
}
