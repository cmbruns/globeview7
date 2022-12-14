import io
import json
from math import atan, cos, cosh, degrees, exp, radians, sin
import pathlib

# import arcgis  # not working for python 3.11 yet Nov 5, 2022
import numpy
from OpenGL import GL
from PIL import Image
import requests

from gv import shader
from gv.layer import ILayer
import gv.vertex_buffer


def _norm(v):
    s = numpy.linalg.norm(v)
    return [x / s for x in v]


# Stencil buffer mask bits
tile_arity_mask = 0b010  # for the current tile, the arity of number of polygons overlapping this pixel
projection_region_mask = 0b100  # all valid pixels on screen for this projection


_debug_tile_boundaries = True


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
        self.fill_color_shader = None
        self.boundary_shader = None
        self.texture_shader = None  # TODO: hoist shaders into Basemap
        self.fill_color_location = None
        self.tile_coord_location = None
        self.contains_antipode_fill_location = None
        self.contains_antipode_edge_location = None
        self.edge_color_location = None
        self.line_width_location = None
        self.basemap = basemap
        self.texture = None
        # compute tile corner locations
        verts_ecf = []
        in_ecf = []
        out_ecf = []
        self.lon_range = [-180, 180]
        self.lat_range = [-90, 90]
        if rez > 0:
            # Corner locations
            verts_ttc = [  # in tile texture coordinates
                [0, 0],  # upper left
                [0.5, 0],  # upper middle
                [1, 0],  # upper right
                [1, 0.5],  # right middle
                [1, 1],  # lower right
                [0.5, 1],  # lower middle
                [0, 1],  # lower left
                [0, 0.5],  # left middle
            ]
            # Directions into and out of the corners
            in_ttc = [
                [0, -1],  # up
                [1, 0],  # right
                [1, 0],  # right
                [0, 1],  # down
                [0, 1],  # down
                [-1, 0],  # left
                [-1, 0],  # left
                [0, -1],  # up
            ]
            out_ttc = [
                [1, 0],  # right
                [1, 0],  # right
                [0, 1],  # down
                [0, 1],  # down
                [-1, 0],  # left
                [-1, 0],  # left
                [0, -1],  # up
                [0, -1],  # up
            ]
            # Mercator coordinates
            k = radians(360 / 2**rez)  # map units per tile index
            o = radians(180)  # origin offset
            verts_mrc = [(k * (x + tx) - o, o - k * (y + ty)) for tx, ty in verts_ttc]
            in_mrc = [_norm([dx, -dy]) for dx, dy in in_ttc]
            out_mrc = [_norm([dx, -dy]) for dx, dy in out_ttc]
            # WGS84 coordinates
            verts_wgs = [(mx, 2 * atan(exp(my)) - radians(90)) for mx, my in verts_mrc]
            in_wgs = []
            out_wgs = []
            for i, p in enumerate(verts_mrc):
                k = 1.0 / cosh(p[1])  # dlat/dy partial derivative
                in_wgs.append(_norm([in_mrc[i][0], k * in_mrc[i][1]]))
                out_wgs.append(_norm([out_mrc[i][0], k * out_mrc[i][1]]))
            # Compute wgs ranges for latitude testing
            lon1 = degrees(verts_wgs[0][0])
            lat1 = degrees(verts_wgs[0][1])
            self.lon_range[:] = (lon1, lon1)
            self.lat_range[:] = (lat1, lat1)
            for w in verts_wgs:
                self.lon_range[0] = min(self.lon_range[0], degrees(w[0]))  # min
                self.lon_range[1] = max(self.lon_range[1], degrees(w[0]))  # max
                self.lat_range[0] = min(self.lat_range[0], degrees(w[1]))  # min
                self.lat_range[1] = max(self.lat_range[1], degrees(w[1]))  # max
            # ECF coordinates
            verts_ecf = [(
                cos(wx) * cos(wy),  # x thither
                sin(wx) * cos(wy),  # y right
                sin(wy),  # z up
            ) for wx, wy in verts_wgs]
            in_ecf = []
            out_ecf = []
            for i, p in enumerate(verts_wgs):
                lon, lat = p[0], p[1]
                # noinspection PyPep8Naming
                dobq_J_dwgs = numpy.array([
                    [-cos(lat) * sin(lon), -sin(lat) * cos(lon)],
                    [cos(lat) * cos(lon), -sin(lat) * sin(lon)],
                    [0, cos(lat)],
                ], dtype=numpy.float64)
                in_ecf.append(_norm(dobq_J_dwgs @ in_wgs[i]))
                out_ecf.append(_norm(dobq_J_dwgs @ out_wgs[i]))
        if len(verts_ecf) == 0:
            self.boundary_vertices = gv.vertex_buffer.VertexBuffer(verts_ecf)
        else:
            self.boundary_vertices = gv.vertex_buffer.VertexBuffer(verts_ecf, in_ecf, out_ecf)
        indexes = []
        nv = len(verts_ecf)
        for i in range(nv - 1):
            indexes.append(i)
            indexes.append(i + 1)
        indexes.extend([nv - 1, 0])  # Close loop
        self.boundary_indexes = numpy.array(indexes, dtype=numpy.int8)
        self.ibo = None

        # TODO: include corner directions in vertex buffer

    def contains_antipode(self, context) -> bool:
        lon, lat = context.center_location  # screen center in WGS84
        assert lon <= 180
        assert lon >= -180
        # rotate to antipode
        lon = lon + 180
        if lon > 180:
            lon = lon - 360
        lat = -lat
        return (self.lon_range[0] <= lon < self.lon_range[1]
                and self.lat_range[0] <= lat <= self.lat_range[1])

    def initialize_opengl(self):
        self.basemap.initialize_opengl()
        self.boundary_vertices.bind()
        self.ibo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ibo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.boundary_indexes, GL.GL_STATIC_DRAW)
        if self.rez == 0:
            self.fill_shader = self.basemap.root_tile_shader
        else:
            self.fill_shader = self.basemap.tile_fill_shader
            self.fill_color_location = GL.glGetUniformLocation(self.fill_shader, "uColor")
            self.boundary_shader = self.basemap.tile_boundary_shader
            self.edge_color_location = GL.glGetUniformLocation(self.boundary_shader, "uColor")
            self.line_width_location = GL.glGetUniformLocation(self.boundary_shader, "uLineWidth")
            self.contains_antipode_edge_location = GL.glGetUniformLocation(self.boundary_shader, "uContainsAntipode")
        self.fill_color_shader = shader.Program(
            shader.Stage(["screen_quad.vert"], GL.GL_VERTEX_SHADER),
            shader.Stage(["color.frag"], GL.GL_FRAGMENT_SHADER),
        ).compile(validate=True)
        self.texture_shader = shader.Program(
            shader.Stage(["screen_quad.vert"], GL.GL_VERTEX_SHADER),
            shader.Stage(["basemap.frag"], GL.GL_FRAGMENT_SHADER),
        ).compile(validate=True)
        self.tile_coord_location = GL.glGetUniformLocation(self.texture_shader, "uTileCoord")
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
            # Wrap around the international date line.
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT)
            # Extend to the poles.
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        else:
            # Draw nothing outside the tile boundaries
            # Set border color to magenta when debugging tile boundaries
            if _debug_tile_boundaries:
                GL.glTexParameterfv(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_BORDER_COLOR, (1, 0, 1, 1))  # Magenta
            else:
                GL.glTexParameterfv(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_BORDER_COLOR, (0, 0, 0, 0))  # Invisible black
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_BORDER)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_BORDER)
        GL.glGenerateMipmap(GL.GL_TEXTURE_2D)
        GL.glBindVertexArray(0)

    def paint_opengl(self, context):
        if self.texture is None:
            self.initialize_opengl()
        self.boundary_vertices.bind()
        GL.glUseProgram(self.fill_shader)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
        if self.rez == 0:
            context.projection.fill_boundary(context, self.fill_shader)
        else:
            raise NotImplementedError

    def fill_boundary(self, context):
        if self.rez == 0:
            context.projection.paint_boundary(context)
            return
        if self.boundary_shader is None:
            self.initialize_opengl()
        # ...3) Populate tile polygon arity stencil mask
        self.boundary_vertices.bind()
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ibo)
        GL.glUseProgram(self.fill_shader)
        GL.glPatchParameteri(GL.GL_PATCH_VERTICES, 2)
        GL.glStencilMask(tile_arity_mask)
        GL.glClear(GL.GL_STENCIL_BUFFER_BIT)
        GL.glColorMask(False, False, False, False)
        GL.glStencilFunc(GL.GL_ALWAYS, 0, tile_arity_mask)
        GL.glStencilOp(GL.GL_KEEP, GL.GL_KEEP, GL.GL_INVERT)
        GL.glDrawElements(GL.GL_PATCHES, len(self.boundary_indexes), GL.GL_UNSIGNED_BYTE, None)
        # 4) Use a cheap vertex shader to fill in the color
        GL.glColorMask(True, True, True, True)
        # TODO: more nuanced antipode signed distance from tile edge test
        if self.contains_antipode(context):
            print("contains antipode")
            ref = projection_region_mask  # Invert polygon area
            msk = tile_arity_mask | projection_region_mask
        else:
            print("does NOT contain antipode")
            ref = tile_arity_mask | projection_region_mask
            msk = tile_arity_mask | projection_region_mask
        GL.glStencilFunc(GL.GL_EQUAL, ref, msk)
        GL.glStencilOp(GL.GL_KEEP, GL.GL_KEEP, GL.GL_KEEP)
        draw_image = True
        if draw_image:
            GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
            GL.glUseProgram(self.texture_shader)
            GL.glUniform3f(self.tile_coord_location, self.x, self.y, self.rez)
        else:
            GL.glUseProgram(self.fill_color_shader)
            GL.glUniform4f(self.fill_color_location, 0, 1, 0, 0.2)  # Transparent green
        GL.glDrawArrays(GL.GL_TRIANGLE_FAN, 0, 4)

    def paint_boundary(self, context):
        if self.rez == 0:
            context.projection.paint_boundary(context)
            return
        if self.boundary_shader is None:
            self.initialize_opengl()
        self.boundary_vertices.bind()
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ibo)
        GL.glUseProgram(self.boundary_shader)
        GL.glUniform4f(self.edge_color_location, 0, 1, 0, 1)  # green
        GL.glUniform1f(self.line_width_location, 4)
        GL.glUniform1i(self.contains_antipode_edge_location, int(self.contains_antipode(context)))
        GL.glPatchParameteri(GL.GL_PATCH_VERTICES, 2)
        # GL.glDrawArrays(GL.GL_PATCHES, 0, len(self.boundary_vertices))
        # GL.glDrawArrays(GL.GL_LINE_LOOP, 0, len(self.boundary_vertices))
        # GL.glDrawElements(GL.GL_LINES, len(self.boundary_indexes), GL.GL_UNSIGNED_BYTE, None)
        GL.glDrawElements(GL.GL_PATCHES, len(self.boundary_indexes), GL.GL_UNSIGNED_BYTE, None)


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
        self.tile_fill_shader = None
        self.tile_boundary_shader = None

    def fetch_tile(self, x, y, rez):
        # TODO: cache tiles
        return WebMercatorTile(x, y, rez, self)

    def initialize_opengl(self):
        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)
        self.root_tile_shader = shader.Program(
            shader.Stage(["basemap.vert"], GL.GL_VERTEX_SHADER),
            shader.Stage(["basemap.frag"], GL.GL_FRAGMENT_SHADER),
        ).compile(validate=True)
        # TODO: is a separate shader needed?
        # Well, separate shaders for outline vs fill are needed...
        # ...and it might be an optimization to avoid gradient texture fetch for non-root tiles
        self.tile_fill_shader = shader.Program(
            shader.Stage(["tile_boundary.vert"], GL.GL_VERTEX_SHADER),
            shader.Stage(["tile_boundary.tesc"], GL.GL_TESS_CONTROL_SHADER),
            shader.Stage(["tile_boundary.tese"], GL.GL_TESS_EVALUATION_SHADER),
            shader.Stage(["tile_fill.geom"], GL.GL_GEOMETRY_SHADER),
            shader.Stage(["color.frag"], GL.GL_FRAGMENT_SHADER),
            # validate=False,
        ).compile(validate=False)
        self.tile_boundary_shader = shader.Program(
            shader.Stage(["tile_boundary.vert"], GL.GL_VERTEX_SHADER),
            shader.Stage(["tile_boundary.tesc"], GL.GL_TESS_CONTROL_SHADER),
            shader.Stage(["tile_boundary.tese"], GL.GL_TESS_EVALUATION_SHADER),
            # shader.Stage(["h3cell.geom"], GL.GL_GEOMETRY_SHADER),
            shader.Stage(["tile_boundary.geom"], GL.GL_GEOMETRY_SHADER),  # TODO: use clipping shader for outline after debugging fill
            shader.Stage(["color.frag"], GL.GL_FRAGMENT_SHADER),
        ).compile(validate=True)
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
    def __init__(self, name: str, tile_coords):
        super().__init__(name=name)
        basemap = Basemap()
        self.tiles = []
        for tc in tile_coords:
            x, y, rez = tc
            self.tiles.append(basemap.fetch_tile(x, y, rez))
        self.vao = None
        self.boundary_shader = None
        self.color_location = None
        # Testing resources
        self.screen_shader = None
        self.color_screen_location = None

    def initialize_opengl(self):
        for tile in self.tiles:
            tile.initialize_opengl()
        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)
        self.boundary_shader = shader.Program(
            shader.Stage(["boundary.vert"], GL.GL_VERTEX_SHADER),
            shader.Stage(["color.frag"], GL.GL_FRAGMENT_SHADER),
        ).compile(validate=True)
        self.color_location = GL.glGetUniformLocation(self.boundary_shader, "uColor")

        # Testing resources
        self.screen_shader = shader.Program(
            shader.Stage(["screen_quad.vert"], GL.GL_VERTEX_SHADER),
            shader.Stage(["color.frag"], GL.GL_FRAGMENT_SHADER),
        ).compile(validate=True)
        self.color_screen_location = GL.glGetUniformLocation(self.screen_shader, "uColor")

        GL.glBindVertexArray(0)

    def paint_opengl(self, context):
        if self.vao is None:
            self.initialize_opengl()
        show_test_render = False
        if show_test_render:
            # TODO: remove this block of render tests
            # 1) color full screen pale red
            GL.glBindVertexArray(self.vao)
            GL.glUseProgram(self.screen_shader)
            GL.glUniform4f(self.color_screen_location, 1, 0, 0, 0.2)  # red full screen
            GL.glDrawArrays(GL.GL_TRIANGLE_FAN, 0, 4)
            # 2) color valid projection area pale green
            GL.glUseProgram(self.boundary_shader)
            GL.glUniform4f(self.color_screen_location, 0, 1, 0, 0.2)  # green valid area
            context.projection.fill_boundary(context, self.boundary_shader)  # TODO:
        # 1) Clear stencil mask
        GL.glEnable(GL.GL_STENCIL_TEST)
        GL.glStencilMask(projection_region_mask | tile_arity_mask)
        GL.glClear(GL.GL_STENCIL_BUFFER_BIT)
        # 2) Mask valid projection region
        GL.glStencilMask(projection_region_mask)
        GL.glStencilFunc(GL.GL_ALWAYS, 0, projection_region_mask)
        GL.glStencilOp(GL.GL_KEEP, GL.GL_KEEP, GL.GL_INVERT)
        GL.glColorMask(False, False, False, False)
        GL.glBindVertexArray(self.vao)
        GL.glUseProgram(self.boundary_shader)
        context.projection.fill_boundary(context, self.boundary_shader)
        # 3) Render the tile(s)
        # TODO: loop over multiple tiles
        for tile in self.tiles:
            tile.fill_boundary(context)
        GL.glDisable(GL.GL_STENCIL_TEST)
        # 4) Draw the outline of the tile(s)
        if _debug_tile_boundaries:
            for tile in self.tiles:
                tile.paint_boundary(context)
