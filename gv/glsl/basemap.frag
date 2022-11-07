#ifndef CUSTOM_PROCESS_INCLUDES
#extension GL_GOOGLE_include_directive : enable
#include "sampler.frag"
#include "projection.glsl"
#endif

in vec3 nmc;

uniform sampler2D image;
uniform vec3 uTileCoord = vec3(0, 0, 0);

out vec4 frag_color;

void main()
{
    vec3 obq = obq_for_nmc(nmc);
    mat3 ecf_X_obq = mat3(ub.ecf_X_obq4);
    vec3 ecf = ecf_X_obq * obq;
    vec2 wgs = wgs_for_ecf(ecf);
    vec3 mercator = vec3(mercator_for_lonlat(wgs), 1);
    // TODO library function for tile coordinates
    float k = pow(2, uTileCoord.z);
    float s = k / radians(360);
    mat3 tile_X_merc = mat3(
        s,  0, 0,
        0, -s, 0,
        k * 0.5 - uTileCoord.x,  k * 0.5 - uTileCoord.y, 1);
    vec3 tile = tile_X_merc * mercator;
    frag_color = catrom(image, tile.xy / tile.z);
}
