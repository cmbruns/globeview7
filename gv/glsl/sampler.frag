#line 2

vec4 catrom_weights(float t) {
    return 0.5 * vec4(
        -1*t*t*t + 2*t*t - 1*t,  // P0 weight
        3*t*t*t - 5*t*t + 2,  // P1 weight
        -3*t*t*t + 4*t*t + 1*t,  // P2 weight
        1*t*t*t - 1*t*t);  // P3 weight
}

vec4 equirect_color(in sampler2D image, in vec2 tex_coord)
{
    // Use explicit gradients, to preserve anisotropic filtering during mipmap lookup
    vec2 dpdx = dFdx(tex_coord);
    vec2 dpdy = dFdy(tex_coord);
    if (true) {
        if (dpdx.x > 0.5) dpdx.x -= 1; // use "repeat" wrapping on gradient
        if (dpdx.x < -0.5) dpdx.x += 1;
        if (dpdy.x > 0.5) dpdy.x -= 1; // use "repeat" wrapping on gradient
        if (dpdy.x < -0.5) dpdy.x += 1;
    }

    return textureGrad(image, tex_coord, dpdx, dpdy);
}

vec4 catrom(sampler2D image, vec2 textureCoordinate)
{
    vec2 texel = textureCoordinate * textureSize(image, 0) - vec2(0.5);
    ivec2 texel1 = ivec2(floor(texel));
    vec2 param = texel - texel1;
    vec4 weightsX = catrom_weights(param.x);
    vec4 weightsY = catrom_weights(param.y);
    vec4 combined = vec4(0);
    // TODO: fewer taps using linear
    for (int y = 0; y < 4; ++y) {
        float wy = weightsY[y];
        for (int x = 0; x < 4; ++x) {
            float wx = weightsX[x];
            vec2 texel2 = vec2(x , y) + texel1 - vec2(0.5);
            vec2 tc = texel2 / textureSize(image, 0);
            combined += wx * wy * equirect_color(image, tc);
        }
    }
    return combined;
}
