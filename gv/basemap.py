import inspect
import io
import requests

import numpy
from OpenGL import GL
from OpenGL.GL.shaders import compileShader, compileProgram
from PIL import Image

from gv import shader


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
        self.shader = compileProgram(
            shader.from_files(["ndc_from_nmc.vert"], GL.GL_VERTEX_SHADER),
            shader.from_files(["projection.glsl", "sampler.frag", "basemap.frag"], GL.GL_FRAGMENT_SHADER),
        )
        self.texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 4)  # 1 interferes with later Qt text rendering
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
        if self.texture is None:
            self.initialize_opengl()
        GL.glUseProgram(self.shader)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
        GL.glUniformMatrix3fv(1, 1, True, context.ndc_X_nmc)
        GL.glUniformMatrix3fv(2, 1, True, context.ecf_X_obq)
        GL.glUniform1i(4, context.projection.index.value)
        context.projection.fill_boundary(context)
