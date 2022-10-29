import io
import json
from math import atan, exp, radians
import pathlib

import arcgis
import numpy
from OpenGL import GL
from OpenGL.GL.shaders import compileProgram
from PIL import Image
import requests

from gv import shader
from gv.layer import ILayer
import gv.vertex_buffer


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
        self.fill_shader = None
        self.boundary_shader = None
        self.basemap = basemap
        self.texture = None
        # compute corner locations
        verts_wgs = []
        if rez > 0:
            verts_ttc = [  # in tile texture coordinates
                [0, 0],  # upper left
                [1, 0],  # upper right
                [1, 1],  # lower right
                [0, 1],  # lower left
            ]
            k = radians(360 / 2**rez)  # map units per tile index
            o = radians(180)  # origin offset
            verts_mrc = [(k * (x + tx) - o, o - k * (y + ty)) for tx, ty in verts_ttc]
            verts_wgs = [(mx, 2 * atan(exp(my)) - radians(90)) for mx, my in verts_mrc]
        self.boundary_vertices = gv.vertex_buffer.VertexBuffer(verts_wgs)
        # TODO: include corner directions in vertex buffer

    def initialize_opengl(self):
        self.basemap.initialize_opengl()
        self.boundary_vertices.bind()
        if self.rez == 0:
            self.fill_shader = self.basemap.root_tile_shader
        else:
            self.fill_shader = self.basemap.tile_shader
            self.boundary_shader = self.basemap.tile_boundary_shader
        self.texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 4)  # 1 interferes with later Qt text rendering
        img = self.image
        GL.glTexImage2D(
            GL.GL_TEXTURE_2D,
            0,
            GL.GL_RGBA,
            img.width,
            img.height,
            0,
            GL.GL_RGBA,
            GL.GL_UNSIGNED_BYTE,
            self.pixels,
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
        self.boundary_vertices.bind()
        GL.glUseProgram(self.fill_shader)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
        if self.rez == 0:
            context.projection.fill_boundary(context)
        else:
            raise NotImplementedError

    def paint_boundary(self, context):
        if self.rez == 0:
            context.projection.paint_boundary(context)
            return
        if self.boundary_shader is None:
            self.initialize_opengl()
        self.boundary_vertices.bind()
        GL.glUseProgram(self.boundary_shader)
        GL.glDrawArrays(GL.GL_LINE_LOOP, 0, len(self.boundary_vertices))


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
        self.vao = None
        self.root_tile_shader = None
        self.tile_shader = None
        self.tile_boundary_shader = None

    def fetch_tile(self, x, y, rez):
        # TODO: cache tiles
        return WebMercatorTile(x, y, rez, self)

    def initialize_opengl(self):
        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)
        self.root_tile_shader = compileProgram(
            shader.from_files(["projection.glsl", "basemap.vert"], GL.GL_VERTEX_SHADER),
            shader.from_files(["projection.glsl", "sampler.frag", "basemap.frag"], GL.GL_FRAGMENT_SHADER),
        )
        ub_index = GL.glGetUniformBlockIndex(self.root_tile_shader, "TransformBlock")
        GL.glUniformBlockBinding(self.root_tile_shader, ub_index, 2)
        # TODO: is a separate shader needed?
        # Well, separate shaders for outline vs fill are needed...
        # ...and it might be an optimization to avoid gradient texture fetch for non-root tiles
        self.tile_shader = compileProgram(
            shader.from_files(["projection.glsl", "basemap.vert"], GL.GL_VERTEX_SHADER),
            shader.from_files(["projection.glsl", "sampler.frag", "basemap.frag"], GL.GL_FRAGMENT_SHADER),
        )
        ub_index = GL.glGetUniformBlockIndex(self.tile_shader, "TransformBlock")
        GL.glUniformBlockBinding(self.tile_shader, ub_index, 2)
        self.tile_boundary_shader = compileProgram(
            shader.from_files(["projection.glsl", "boundary_wgs.vert"], GL.GL_VERTEX_SHADER),
            shader.from_files(["red.frag"], GL.GL_FRAGMENT_SHADER),
        )
        ub_index = GL.glGetUniformBlockIndex(self.tile_boundary_shader, "TransformBlock")
        GL.glUniformBlockBinding(self.tile_boundary_shader, ub_index, 2)
        GL.glBindVertexArray(0)


class RootRasterTile(ILayer):
    def __init__(self, name: str):
        super().__init__(name=name)
        basemap = Basemap()
        self.tile = basemap.fetch_tile(0, 0, 0)

    def initialize_opengl(self):
        self.tile.initialize_opengl()

    def paint_opengl(self, context):
        self.tile.paint_opengl(context)


class TestRasterTile(ILayer):
    def __init__(self, name: str, x, y, rez):
        super().__init__(name=name)
        basemap = Basemap()
        self.tile = basemap.fetch_tile(x, y, rez)

    def initialize_opengl(self):
        self.tile.initialize_opengl()

    def paint_opengl(self, context):
        self.tile.paint_boundary(context)
