# line 2

// call with GL.glDrawArrays(GL.GL_TRIANGLE_FAN, 0, 4)

uniform vec4 uColor = vec4(0, 0, 1, 0.3);
out vec4 fColor;

const vec4 corner[] = vec4[](
    vec4(-1, +1, 0.5, 1),
    vec4(+1, +1, 0.5, 1),
    vec4(+1, -1, 0.5, 1),
    vec4(-1, -1, 0.5, 1));

void main()
{
    gl_Position = corner[gl_VertexID];
    fColor = uColor;
}
