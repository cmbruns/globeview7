import inspect
import pkg_resources

from OpenGL.GL.shaders import compileShader, compileProgram


class Shader(object):
    pass


def string_from_file(file_name):
    string = pkg_resources.resource_string("gv.glsl", file_name).decode()
    return string


def from_files(file_names, stage):
    files = ["version.glsl"]
    files.extend(file_names)
    return compileShader(
        "\n".join([string_from_file(f) for f in files]),
        stage)


def from_string(string, stage):
    return compileShader(inspect.cleandoc(string), stage)
