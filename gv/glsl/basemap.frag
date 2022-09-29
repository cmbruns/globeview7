#line 2

in vec3 nmc;

uniform sampler2D image;

out vec4 frag_color;

void main()
{
    vec3 obq = obq_for_nmc(nmc, ub.projection);
    mat3 ecf_X_obq = mat3(ub.ecf_X_obq4);
    vec3 ecf = ecf_X_obq * obq;
    vec2 wgs = wgs_for_ecf(ecf);
    vec2 mercator = mercator_for_lonlat(wgs);
    // TODO library function for tile coordinates
    vec2 tile = mercator;
    tile.y *= -1;
    tile = tile / radians(360) + vec2(0.5);
    frag_color = catrom(image, tile);
}
