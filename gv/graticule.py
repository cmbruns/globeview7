from OpenGL import GL
from OpenGL.GL.shaders import compileProgram

from gv.layer import ILayer
from gv import shader
from gv.vertex_buffer import VertexBuffer


class Graticule(ILayer):
    def __init__(self, name:str):
        super().__init__(name=name)
        self.shader = None
        self.vertices = None

    def initialize_opengl(self):
        if self.shader is not None:
            return
        self.shader = compileProgram(
            shader.from_files(["coastline.vert", ], GL.GL_VERTEX_SHADER),
            shader.from_files(["projection.glsl", "coastline.geom", ], GL.GL_GEOMETRY_SHADER),
            shader.from_files(["coastline.frag", ], GL.GL_FRAGMENT_SHADER),
        )
        polygons = []
        # Parallels
        nsegs = 100
        for lat in [0]:  # TODO: more parallels
            polygon = []
            for segment in range(nsegs):
                polygon.append([360 * segment / nsegs, lat])
            polygons.extend(polygon)
        self.vertices = VertexBuffer(polygons)
        # TODO: meridians

    def paint_opengl(self, context):
        if self.shader is None:
            self.initialize_opengl()
        GL.glUseProgram(self.shader)
        GL.glLineWidth(1)
        self.vertices.bind()
        GL.glDrawArrays(GL.GL_LINE_LOOP, 0, len(self.vertices))
