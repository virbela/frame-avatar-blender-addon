in vec4 color;
in vec3 position;
in vec4 bone_weights;
in vec4 bone_indices;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec4 fcolor;

int isMatZero(mat4 m);

void main() {
    fcolor = color;
    gl_Position = projection * view * model * vec4(position, 1.0);
}

int isMatZero(mat4 m) {
    int result = 1;
    for (int i = 0; i < 4; i++) {
        if (m[i] != vec4(0.0)) {
            result = 0;
            break;
        }
    }
    return result;
}
