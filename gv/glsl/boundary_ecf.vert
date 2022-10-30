layout (location = 0) in vec3 pos_ecf_in;  // vertex position
layout (location = 1) in vec3 inDir_ecf_in;  // vertex incoming direction
layout (location = 2) in vec3 outDir_ecf_in;  // vertex outgoing direction

flat out vec3 inDir_ecf;
flat out vec3 outDir_ecf;

void main()
{
    gl_Position = vec4(pos_ecf_in, 1);
    inDir_ecf = inDir_ecf_in;
    outDir_ecf = outDir_ecf_in;
}
