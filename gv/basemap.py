import inspect

from OpenGL import GL
from OpenGL.GL.shaders import compileShader, compileProgram


class RootRasterTile(object):
    def __init__(self):
        self.vao = None
        self.shader = None

    def initialize_opengl(self):
        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)
        self.shader = compileProgram(
            compileShader(inspect.cleandoc("""
                #version 430
                
                const vec3 nmcBounds[4] = vec3[](
                    vec3(-1, -1, 1),
                    vec3(-1, +1, 1),
                    vec3(+1, +1, 1),
                    vec3(+1, -1, 1));

                const vec2 wgsBounds[4] = vec2[](
                    vec2(radians(-90), radians(-90)),
                    vec2(radians(-90), radians(+90)),
                    vec2(radians(+90), radians(+90)),
                    vec2(radians(+90), radians(-90)));
               
                layout(location = 1) uniform mat3 ndc_X_nmc = mat3(1);
                layout(location = 2) uniform mat3 obq_X_ecf = mat3(1);
                const int WGS84_PROJECTION = 0;
                const int ORTHOGRAPHIC_PROJECTION = 1;
                layout(location = 4) uniform int projection = WGS84_PROJECTION;
                
                void main() {
                    vec2 wgs = wgsBounds[gl_VertexID];
                    vec3 ecf = vec3(
                        cos(wgs.x) * cos(wgs.y),
                        sin(wgs.x) * cos(wgs.y),
                        sin(wgs.y));
                    vec3 obq = obq_X_ecf * ecf;
                    vec3 nmc;
                    if (projection == ORTHOGRAPHIC_PROJECTION) {
                        nmc = vec3(obq.y, obq.z, 1);
                    }
                    else if (projection == WGS84_PROJECTION) {
                        nmc = vec3(
                            atan(obq.y, obq.x),
                            asin(obq.z),
                            1);
                    }
                    
                    // TODO: these transforms are not working.
                    // nmc = vec3(wgs, 1);  // ok
                    // nmc = vec3(obq.y, obq.z, 1); // nothing...
                    nmc = vec3(ecf.y, ecf.z, 1); // nothing
                    vec3 ndc = ndc_X_nmc * nmc;
                    
                    // vec3 ndc = ndc_X_nmc * nmcBounds[gl_VertexID];  // ok
                    
                    gl_Position = vec4(ndc.xy, 0, ndc.z);
                }
            """), GL.GL_VERTEX_SHADER),
            compileShader(inspect.cleandoc("""
                #version 430
                
                out vec4 frag_color;
                
                void main() {
                    frag_color = vec4(0, 1, 0, 1);
                }
        """), GL.GL_FRAGMENT_SHADER),
        )
        GL.glBindVertexArray(0)

    def paint_opengl(self, context):
        if self.vao is None:
            self.initialize_opengl()
        GL.glBindVertexArray(self.vao)
        GL.glUseProgram(self.shader)
        GL.glUniformMatrix3fv(1, 1, True, context.ndc_X_nmc)
        GL.glUniformMatrix3fv(2, 1, False, context.ecf_X_obq)  # transpose is inverse
        GL.glUniform1i(4, context.projection.index.value)
        GL.glDrawArrays(GL.GL_TRIANGLE_FAN, 0, 4)
        GL.glBindVertexArray(0)
