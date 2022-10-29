import io
import json
import pathlib

import arcgis
import numpy
from OpenGL import GL
from OpenGL.GL.shaders import compileProgram
from PIL import Image
import requests

from gv import shader
from gv.layer import ILayer


class WebMercatorTile(object):
    def __init__(self, x, y, rez, basemap):
        self.x = x
        self.y = y
        self.rez = rez
        tile_url = basemap.raster_tile_url.format(x=x, y=y, z=rez)
        response = requests.get(url=tile_url)
        data = io.BytesIO(response.content)
        self.image = Image.open(data)
        self.pixels = numpy.frombuffer(
            buffer=self.image.convert("RGBA").tobytes(), dtype=numpy.ubyte
        )
        self.vao = None
        self.shader = None
        self.basemap = basemap
        self.texture = None

    def initialize_opengl(self):
        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)
        self.basemap.initialize_opengl()
        if self.rez == 0:
            self.shader = self.basemap.root_tile_shader
        else:
            self.shader = self.basemap.tile_shader
        ub_index = GL.glGetUniformBlockIndex(self.shader, "TransformBlock")
        GL.glUniformBlockBinding(self.shader, ub_index, 2)
        self.texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 4)  # 1 interferes with later Qt text rendering
        img = self.tile.image
        GL.glTexImage2D(
            GL.GL_TEXTURE_2D,
            0,
            GL.GL_RGBA,
            img.width,
            img.height,
            0,
            GL.GL_RGBA,
            GL.GL_UNSIGNED_BYTE,
            self.tile.pixels,
        )
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR_MIPMAP_LINEAR)
        if self.rez == 0:
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT)
        else:
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        GL.glGenerateMipmap(GL.GL_TEXTURE_2D)
        GL.glBindVertexArray(0)

    def paint_opengl(self, context):
        if self.texture is None:
            self.initialize_opengl()
        GL.glBindVertexArray(self.vao)
        GL.glUseProgram(self.shader)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
        if self.rez == 0:
            context.projection.fill_boundary(context)
        else:
            raise NotImplementedError


class Basemap(object):
    def __init__(self, basemap_style="ArcGIS:Imagery"):
        self.style = basemap_style
        # Read personal access token from outside of source control
        with open(f"{pathlib.Path.home()}/biospud_arcgis_api_key.txt") as fh:
            access_token = fh.read().strip()
        # https://developers.arcgis.com/documentation/mapping-apis-and-services/maps/services/basemap-layer-service/
        basemap_type = "style"  # Mapbox style json
        url = f"https://basemaps-api.arcgis.com/arcgis/rest/services/styles/" \
              f"{self.style}?type={basemap_type}&token={access_token}"
        # Fetch raster tile url
        r = requests.get(url=url)
        j = r.json()
        # print(json.dumps(j, indent=2))
        self.raster_tile_url = None
        sources = j["sources"]
        for source, content in sources.items():
            if content["type"] == "raster":
                self.raster_tile_url = content["tiles"][0]
                self.attribution = content["attribution"]
                break
        assert self.raster_tile_url is not None

    def fetch_tile(self, x, y, rez):
        # TODO: cache tiles
        return WebMercatorTile(x, y, rez, self)


class RootRasterTile(ILayer):
    def __init__(self, name: str):
        super().__init__(name=name)
        self.vao = None
        self.shader = None
        self.texture = None
        connection = Basemap()
        self.tile = connection.fetch_tile(0, 0, 0)

    def initialize_opengl(self):
        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)
        self.shader = compileProgram(
            shader.from_files(["projection.glsl", "basemap.vert"], GL.GL_VERTEX_SHADER),
            shader.from_files(["projection.glsl", "sampler.frag", "basemap.frag"], GL.GL_FRAGMENT_SHADER),
        )
        ub_index = GL.glGetUniformBlockIndex(self.shader, "TransformBlock")
        GL.glUniformBlockBinding(self.shader, ub_index, 2)
        self.texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 4)  # 1 interferes with later Qt text rendering
        img = self.tile.image
        GL.glTexImage2D(
            GL.GL_TEXTURE_2D,
            0,
            GL.GL_RGBA,
            img.width,
            img.height,
            0,
            GL.GL_RGBA,
            GL.GL_UNSIGNED_BYTE,
            self.tile.pixels,
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
        GL.glBindVertexArray(self.vao)
        GL.glUseProgram(self.shader)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
        context.projection.fill_boundary(context)
