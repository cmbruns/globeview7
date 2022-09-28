import numpy
from OpenGL import GL


class VertexBuffer(object):
    def __init__(self, vertices):
        self.vao = None
        self.vbo = None
        self.vertex_count = len(vertices)
        self.element_count = len(vertices[0])
        self.vertices = numpy.array(vertices, dtype=numpy.float32).flatten()

    def __enter__(self):
        if self.vao is None:
            self.initialize_opengl()
        GL.glBindVertexArray(self.vao)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        GL.glBindVertexArray(0)

    def __len__(self):
        return self.vertex_count

    def initialize_opengl(self):
        if self.vao is None:
            self.vao = GL.glGenVertexArrays(1)
            GL.glBindVertexArray(self.vao)
            self.vbo = GL.glGenBuffers(1)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
            GL.glBufferData(GL.GL_ARRAY_BUFFER, self.vertices, GL.GL_STATIC_DRAW)
            GL.glEnableVertexAttribArray(0)
            GL.glVertexAttribPointer(0, self.element_count, GL.GL_FLOAT, False, 0, None)
            GL.glBindVertexArray(0)
