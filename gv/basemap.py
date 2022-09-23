import inspect
import io
import requests

import numpy
from OpenGL import GL
from OpenGL.GL.shaders import compileShader, compileProgram
from PIL import Image


class RootRasterTile(object):
    def __init__(self):
        self.vao = None
        self.shader = None
        self.texture = None
        # Read personal access token from outside of source control
        with open("C:/Users/cmbruns/biospud_arcgis_api_key.txt") as fh:
            access_token = fh.read().strip()
        # https://developers.arcgis.com/documentation/mapping-apis-and-services/maps/services/basemap-layer-service/
        basemap_style = "ArcGIS:Imagery"
        basemap_type = "style"  # Mapbox style json
        url = f"https://basemaps-api.arcgis.com/arcgis/rest/services/styles/" \
              f"{basemap_style}?type={basemap_type}&token={access_token}"
        # Fetch raster tile url
        r = requests.get(url=url)
        j = r.json()
        # print(json.dumps(j, indent=2))
        raster_tile_url = None
        sources = j["sources"]
        for source, content in sources.items():
            if content["type"] == "raster":
                raster_tile_url = content["tiles"][0]
                break
        # Fetch root tile
        x = y = z = 0
        tile_url = raster_tile_url.format(x=x, y=y, z=z)
        response = requests.get(url=tile_url)
        self.image = Image.open(io.BytesIO(response.content))
        self.pixels = numpy.frombuffer(
            buffer=self.image.convert("RGBA").tobytes(), dtype=numpy.ubyte
        )

    def initialize_opengl(self):
        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)
        self.shader = compileProgram(
            compileShader(inspect.cleandoc("""
                #version 430
                
                // WGS84 projection bounds
                const vec3 nmcWgs84Bounds[4] = vec3[](
                    vec3(0, -radians(90), 1),  // center of northern boundary
                    vec3(-1, 0, 0),  // infinity west
                    vec3(0, +radians(90), 1),  // center of southern boundary
                    vec3(+1, 0, 0));  // infinity east

                layout(location = 1) uniform mat3 ndc_X_nmc = mat3(1);
                const int WGS84_PROJECTION = 0;
                const int ORTHOGRAPHIC_PROJECTION = 1;
                layout(location = 4) uniform int projection = WGS84_PROJECTION;
                
                out vec3 nmc;
                
                void main() {
                    nmc = nmcWgs84Bounds[gl_VertexID];
                    vec3 ndc = ndc_X_nmc * nmc;
                    gl_Position = vec4(ndc.xy, 0, ndc.z);
                }
            """), GL.GL_VERTEX_SHADER),
            compileShader(inspect.cleandoc("""
                #version 430
                
                in vec3 nmc;

                layout(location = 2) uniform mat3 ecf_X_obq = mat3(1);
                const int WGS84_PROJECTION = 0;
                const int ORTHOGRAPHIC_PROJECTION = 1;
                layout(location = 4) uniform int projection = WGS84_PROJECTION;
                uniform sampler2D image;

                out vec4 frag_color;
                
                vec4 catrom_weights(float t) {
                    return 0.5 * vec4(
                        -1*t*t*t + 2*t*t - 1*t,  // P0 weight
                        3*t*t*t - 5*t*t + 2,  // P1 weight
                        -3*t*t*t + 4*t*t + 1*t,  // P2 weight
                        1*t*t*t - 1*t*t);  // P3 weight
                }
                
                vec4 equirect_color(sampler2D image, vec2 tex_coord)
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
                
                vec4 catrom(sampler2D image, vec2 textureCoordinate) {
                    vec2 texel = textureCoordinate * textureSize(image, 0) - vec2(0.5);
                    ivec2 texel1 = ivec2(floor(texel));
                    vec2 param = texel - texel1;
                    // return vec4(param, 0, 1);  // interpolation parameter
                    vec4 weightsX = catrom_weights(param.x);
                    vec4 weightsY = catrom_weights(param.y);
                    // return vec4(-3 * weightsX[3], 0, 0, 1);  // point 1 x weight
                    vec4 combined = vec4(0);
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
                
                void main() 
                {
                    vec2 prj = nmc.xy / nmc.z;  // TODO: wgs84 display projection only
                    
                    vec3 obq = vec3(
                        cos(prj.x) * cos(prj.y),
                        sin(prj.x) * cos(prj.y),
                        sin(prj.y));
                    vec3 ecf = ecf_X_obq * obq;
                    vec2 wgs = vec2(
                        atan(ecf.y, ecf.x),
                        asin(ecf.z));
                    vec2 mercator = vec2(wgs.x, log(tan(radians(45) + wgs.y/2.0)));
                    vec2 tile = mercator;
                    tile.y *= -1;
                    tile = tile / radians(360) + vec2(0.5);

                    // frag_color = vec4(mercator, 0.0, 1);
                    // frag_color = texture(image, tile);
                    frag_color = catrom(image, tile);
                }
        """), GL.GL_FRAGMENT_SHADER),
        )
        self.texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)
        GL.glTexImage2D(
            GL.GL_TEXTURE_2D,
            0,
            GL.GL_RGBA,
            self.image.width,
            self.image.height,
            0,
            GL.GL_RGBA,
            GL.GL_UNSIGNED_BYTE,
            self.pixels,
        )
        # TODO: catmull rom interpolation
        GL.glTexParameteri(
            GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR
        )
        GL.glTexParameteri(
            GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR_MIPMAP_LINEAR
        )
        GL.glTexParameteri(
            GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT
        )
        GL.glTexParameteri(
            GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE
        )
        GL.glGenerateMipmap(GL.GL_TEXTURE_2D)
        GL.glBindVertexArray(0)

    def paint_opengl(self, context):
        if self.vao is None:
            self.initialize_opengl()
        GL.glBindVertexArray(self.vao)
        GL.glUseProgram(self.shader)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
        GL.glUniformMatrix3fv(1, 1, True, context.ndc_X_nmc)
        GL.glUniformMatrix3fv(2, 1, True, context.ecf_X_obq)
        GL.glUniform1i(4, context.projection.index.value)
        GL.glDrawArrays(GL.GL_TRIANGLE_FAN, 0, 4)
        GL.glBindVertexArray(0)
